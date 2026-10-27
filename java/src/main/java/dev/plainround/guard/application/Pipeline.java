package dev.plainround.guard.application;

import dev.plainround.guard.domain.Guarding;
import dev.plainround.guard.domain.Llm.ChatModel;
import dev.plainround.guard.domain.Llm.ChatRequest;
import dev.plainround.guard.domain.Llm.Message;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

/** The input guard, the output guard and the guard layer around the assistant (a port of guards.py and pipeline.py). */
public final class Pipeline {

    public static final String REFUSAL = "I'm sorry, I can't help with that request. I can help with your own orders and with our returns, refunds, "
            + "delivery and cancellation policies.";

    public record Flags(boolean redact, boolean inputGuard, boolean dataScan, boolean outputGuard) {
        public static Flags guarded() {
            return new Flags(true, true, true, true);
        }

        public static Flags bare() {
            return new Flags(false, false, false, false);
        }
    }

    public record Request(String customer, String message, int seed, String helpPage, String noteOrder, String note) {}

    public record Response(String reply, boolean blocked, String stage, List<String> reasons, String rawReply, boolean toolCalled, List<String> unresolved) {}

    /** Labels a message allow or block with a small model. */
    public static final class Classifier {
        private final ChatModel model;
        private final PromptStore prompts;
        private final String modelId;

        public Classifier(ChatModel model, PromptStore prompts, String modelId) {
            this.model = model;
            this.prompts = prompts;
            this.modelId = modelId;
        }

        public String classify(String message) {
            String prompt = Templates.render(prompts.get("input_guard.v2"), Map.of("message", message));
            String text = model.complete(new ChatRequest(modelId, List.of(new Message("user", prompt)), 0.0, 4, null)).text().toUpperCase();
            return text.contains("BLOCK") ? "block" : "allow";
        }
    }

    private final Assistant assistant;
    private final Classifier classifier;
    private final String canary;
    private final Function<String, Iterable<String>> forbiddenFor;
    private final boolean checkCanary;
    private final Flags flags;

    public Pipeline(Assistant assistant, Classifier classifier, String canary, Function<String, Iterable<String>> forbiddenFor, boolean checkCanary, Flags flags) {
        this.assistant = assistant;
        this.classifier = classifier;
        this.canary = canary;
        this.forbiddenFor = forbiddenFor;
        this.checkCanary = checkCanary;
        this.flags = flags;
    }

    public String systemPrompt(String customer) {
        return assistant.systemPrompt(customer);
    }

    public static List<String> scanData(String text) {
        return Guarding.scan(text);
    }

    public Response respond(Request request, List<String> customerValues) {
        Map<String, String> mapping = new LinkedHashMap<>();
        String text = request.message();
        if (flags.redact()) {
            text = Guarding.redact(request.message(), mapping);
        }
        if (flags.inputGuard()) {
            List<String> hits = Guarding.scan(text);
            if (!hits.isEmpty()) {
                return refuse("input", hits, "", false);
            }
            if (Guarding.hasSoftSignal(text) && classifier.classify(text).equals("block")) {
                return refuse("input", List.of("classifier"), "", false);
            }
        }
        Map<String, String> dataMapping = new LinkedHashMap<>(mapping);
        Assistant.Turn turn = new Assistant.Turn(request.customer(), text, request.seed(), request.helpPage(), request.noteOrder(), request.note());
        Function<String, String> redactData = flags.redact() ? data -> Guarding.redact(data, dataMapping) : null;
        Assistant.Result result = assistant.answer(turn, redactData);
        if (!result.flagged().isEmpty()) {
            return refuse("data", result.flagged(), "", result.toolCalled());
        }
        String raw = result.reply();
        if (flags.outputGuard()) {
            List<String> reasons = new ArrayList<>();
            if (checkCanary && Guarding.canaryLeaked(raw, canary)) {
                reasons.add("canary");
            }
            if (!Guarding.foreignValuesIn(raw, forbiddenFor.apply(request.customer())).isEmpty()) {
                reasons.add("foreign_identifier");
            }
            if (Guarding.promptOverlap(raw, assistant.systemPrompt(request.customer()))) {
                reasons.add("prompt_overlap");
            }
            if (!reasons.isEmpty()) {
                return refuse("output", reasons, raw, result.toolCalled());
            }
        }
        Map<String, String> allowed = new LinkedHashMap<>();
        for (Map.Entry<String, String> e : dataMapping.entrySet()) {
            if (mapping.containsKey(e.getKey()) || customerValues.contains(e.getValue())) {
                allowed.put(e.getKey(), e.getValue());
            }
        }
        if (!flags.redact()) {
            return new Response(raw, false, null, List.of(), raw, result.toolCalled(), List.of());
        }
        Map.Entry<String, List<String>> scrubbed = Guarding.scrub(Guarding.restore(raw, allowed));
        return new Response(scrubbed.getKey(), false, null, List.of(), raw, result.toolCalled(), scrubbed.getValue());
    }

    private Response refuse(String stage, List<String> reasons, String raw, boolean toolCalled) {
        return new Response(REFUSAL, true, stage, reasons, raw, toolCalled, List.of());
    }
}
