package dev.plainround.guard.application;

import dev.plainround.guard.domain.Guarding;
import dev.plainround.guard.domain.Llm.ChatModel;
import dev.plainround.guard.domain.Llm.ChatRequest;
import dev.plainround.guard.domain.Llm.ChatResponse;
import dev.plainround.guard.domain.Llm.Message;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** The sample support assistant: a system prompt with a canary, and a read-only find_order tool played by the runtime (a port of assistant.py). */
public final class Assistant {

    private static final Pattern ORDER_ID = Pattern.compile("\\bPR-\\d+\\b");

    public record Turn(String customer, String message, int seed, String helpPage, String noteOrder, String note) {}

    public record Result(String reply, boolean toolCalled, List<String> flagged) {}

    private final ChatModel model;
    private final PromptStore prompts;
    private final String modelId;
    private final String canary;
    private final OrderLookup orders;
    private final double temperature;
    private final Function<String, List<String>> dataScan;

    public Assistant(ChatModel model, PromptStore prompts, String modelId, String canary, OrderLookup orders, double temperature, Function<String, List<String>> dataScan) {
        this.model = model;
        this.prompts = prompts;
        this.modelId = modelId;
        this.canary = canary;
        this.orders = orders;
        this.temperature = temperature;
        this.dataScan = dataScan;
    }

    public String systemPrompt(String customer) {
        return Templates.render(prompts.get("assistant.v1"), Map.of("customer", customer, "canary", canary));
    }

    public Result answer(Turn turn, Function<String, String> redactData) {
        List<String> blocks = new ArrayList<>();
        if (turn.helpPage() != null && !turn.helpPage().isEmpty()) {
            List<String> flagged = dataScan == null ? List.of() : dataScan.apply(turn.helpPage());
            if (!flagged.isEmpty()) {
                return new Result("", false, flagged);
            }
            String page = redactData == null ? turn.helpPage() : redactData.apply(turn.helpPage());
            blocks.add(Guarding.wrapData("HELP_PAGE", page));
        }
        boolean toolCalled = false;
        Matcher m = ORDER_ID.matcher(turn.message());
        LinkedHashSet<String> ids = new LinkedHashSet<>();
        while (m.find()) {
            ids.add(m.group());
        }
        for (String orderId : ids) {
            String record = orders.find(orderId, orderId.equals(turn.noteOrder()) ? turn.note() : null);
            if (record == null) {
                record = "no order " + orderId;
            }
            toolCalled = true;
            List<String> flagged = dataScan == null ? List.of() : dataScan.apply(record);
            if (!flagged.isEmpty()) {
                return new Result("", true, flagged);
            }
            String shown = redactData == null ? record : redactData.apply(record);
            blocks.add(Guarding.wrapData("TOOL_RESULT", shown));
        }
        List<String> parts = new ArrayList<>(blocks);
        parts.add(turn.message());
        String userText = blocks.isEmpty() ? turn.message() : String.join("\n", parts);
        ChatResponse response = model.complete(new ChatRequest(
                modelId, List.of(new Message("system", systemPrompt(turn.customer())), new Message("user", userText)), temperature, 200, turn.seed()));
        return new Result(response.text().strip(), toolCalled, List.of());
    }
}
