package dev.plainround.guard.interfaces;

import dev.plainround.guard.application.Assistant;
import dev.plainround.guard.application.Pipeline;
import dev.plainround.guard.application.PromptStore;
import dev.plainround.guard.application.Suites;
import dev.plainround.guard.application.Suites.CaseRun;
import dev.plainround.guard.domain.Llm.ChatModel;
import dev.plainround.guard.domain.Shop.AttackCase;
import dev.plainround.guard.domain.Shop.BenignCase;
import dev.plainround.guard.infrastructure.DataFiles;
import dev.plainround.guard.infrastructure.FilePrompts;
import dev.plainround.guard.infrastructure.RecordedChatModel;
import dev.plainround.guard.infrastructure.SpringAiChatModel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import tools.jackson.databind.SerializationFeature;
import tools.jackson.databind.json.JsonMapper;

/** Runs both suites against the bare and the guarded assistant from the same files as Python and writes baseline.json, guarded.json and comparison.json. */
public final class Main {

    private Main() {}

    public static void main(String[] args) throws Exception {
        Map<String, String> flags = new LinkedHashMap<>();
        for (int i = 0; i + 1 < args.length; i += 2) {
            flags.put(args[i].replaceFirst("^--", ""), args[i + 1]);
        }
        Path data = Path.of(flags.getOrDefault("data", "data"));
        Path out = Path.of(flags.getOrDefault("out", "reports/java"));
        PromptStore prompts = new FilePrompts(Path.of(flags.getOrDefault("prompts", "prompts")));
        ChatModel model = "recorded".equals(env("LLM_PROVIDER", "recorded"))
                ? new RecordedChatModel(Path.of(flags.getOrDefault("fixtures", "tests/fixtures")))
                : new SpringAiChatModel(env("LLM_BASE_URL", "http://localhost:11434/v1"), env("OPENAI_API_KEY", ""));
        String assistantModel = env("ASSISTANT_MODEL", "qwen2.5:1.5b");
        String guardModel = env("GUARD_MODEL", "qwen2.5:1.5b");
        double temperature = Double.parseDouble(env("TEMPERATURE", "0.7"));
        int runs = Integer.parseInt(env("RUNS", "3"));
        DataFiles shop = new DataFiles(data);
        String canary = DataFiles.loadCanary(data);
        double limit = DataFiles.loadLimit(Path.of(flags.getOrDefault("evals", "evals")));
        List<AttackCase> attacks = DataFiles.loadAttacks(data);
        List<BenignCase> benign = DataFiles.loadBenign(data);

        Map<String, Object> baseline = side(pipeline(model, prompts, assistantModel, guardModel, temperature, canary, shop, false), attacks, benign, canary, shop, runs, limit);
        Map<String, Object> guarded = side(pipeline(model, prompts, assistantModel, guardModel, temperature, canary, shop, true), attacks, benign, canary, shop, runs, limit);
        Map<String, Object> comparison = new LinkedHashMap<>();
        comparison.put("before", baseline.get("families"));
        comparison.put("after", guarded.get("families"));
        comparison.put("benign_before", baseline.get("benign"));
        comparison.put("benign_after", guarded.get("benign"));
        comparison.put("false_block_limit", limit);

        Files.createDirectories(out);
        JsonMapper json = JsonMapper.builder().enable(SerializationFeature.INDENT_OUTPUT).enable(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS).build();
        Files.writeString(out.resolve("baseline.json"), json.writeValueAsString(baseline) + "\n", StandardCharsets.UTF_8);
        Files.writeString(out.resolve("guarded.json"), json.writeValueAsString(guarded) + "\n", StandardCharsets.UTF_8);
        Files.writeString(out.resolve("comparison.json"), json.writeValueAsString(comparison) + "\n", StandardCharsets.UTF_8);
        System.out.println("java: wrote " + out);
    }

    private static Pipeline pipeline(ChatModel model, PromptStore prompts, String assistantModel, String guardModel, double temperature, String canary, DataFiles shop, boolean guarded) {
        Pipeline.Flags flags = guarded ? Pipeline.Flags.guarded() : Pipeline.Flags.bare();
        Assistant assistant = new Assistant(model, prompts, assistantModel, canary, shop, temperature, flags.dataScan() ? Pipeline::scanData : null);
        return new Pipeline(assistant, new Pipeline.Classifier(model, prompts, guardModel), canary, shop::forbiddenFor, true, flags);
    }

    private static Map<String, Object> side(Pipeline pipeline, List<AttackCase> attacks, List<BenignCase> benign, String canary, DataFiles shop, int runs, double limit) {
        List<CaseRun> attackRows = Suites.runAttacks(attacks, pipeline, canary, shop::ownValues, runs);
        List<CaseRun> benignRows = Suites.runBenign(benign, pipeline, shop::ownValues, runs);
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("runs", runs);
        summary.put("families", Suites.familyRates(attackRows, runs));
        summary.put("benign", Suites.benignSummary(benignRows, limit));
        summary.put("input_guard_confusion", Suites.confusion(attackRows, benignRows));
        return summary;
    }

    private static String env(String name, String fallback) {
        String value = System.getenv(name);
        return value == null || value.isBlank() ? fallback : value;
    }
}
