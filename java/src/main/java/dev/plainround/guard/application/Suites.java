package dev.plainround.guard.application;

import dev.plainround.guard.domain.Guarding;
import dev.plainround.guard.domain.Shop.AttackCase;
import dev.plainround.guard.domain.Shop.BenignCase;
import dev.plainround.guard.domain.Shop.Family;
import dev.plainround.guard.domain.Stats;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.function.Function;

/** Running the two suites and the rates they produce (a port of suites.py). */
public final class Suites {

    private Suites() {}

    public record CaseRun(
            String caseId, String kind, String family, boolean risky, int run, boolean succeeded, String evidence,
            boolean blocked, String stage, List<String> reasons, boolean toolCalled, List<String> unresolved) {}

    public record Rate(int successes, int trials, double value, double low, double high) {}

    public static Rate rate(int successes, int trials) {
        Stats.Interval w = Stats.wilson(successes, trials);
        return new Rate(successes, trials, trials == 0 ? 0.0 : (double) successes / trials, w.low(), w.high());
    }

    public static List<CaseRun> runAttacks(List<AttackCase> cases, Pipeline pipeline, String canary, Function<String, List<String>> ownValues, int runs) {
        List<CaseRun> rows = new ArrayList<>();
        for (AttackCase c : cases) {
            for (int run = 1; run <= runs; run++) {
                Pipeline.Response r = pipeline.respond(new Pipeline.Request(c.customer(), c.message(), run, c.helpPage(), c.noteOrder(), c.note()), ownValues.apply(c.customer()));
                String effect = Guarding.attackEffect(c, r.reply(), canary, pipeline.systemPrompt(c.customer()));
                rows.add(new CaseRun(c.caseId(), "attack", c.family().value(), false, run, effect != null, effect == null ? "none" : effect,
                        r.blocked(), r.stage() == null ? "" : r.stage(), r.reasons(), r.toolCalled(), r.unresolved()));
            }
        }
        return rows;
    }

    public static List<CaseRun> runBenign(List<BenignCase> cases, Pipeline pipeline, Function<String, List<String>> ownValues, int runs) {
        List<CaseRun> rows = new ArrayList<>();
        for (BenignCase c : cases) {
            for (int run = 1; run <= runs; run++) {
                Pipeline.Response r = pipeline.respond(new Pipeline.Request(c.customer(), c.message(), run, null, null, null), ownValues.apply(c.customer()));
                rows.add(new CaseRun(c.caseId(), "benign", "benign", c.risky(), run, false, "none", r.blocked(), r.stage() == null ? "" : r.stage(), r.reasons(), r.toolCalled(), r.unresolved()));
            }
        }
        return rows;
    }

    public static Map<String, Object> familyRates(List<CaseRun> rows, int runs) {
        Map<String, Object> out = new LinkedHashMap<>();
        for (Family family : Family.values()) {
            List<CaseRun> subset = rows.stream().filter(r -> r.family().equals(family.value())).toList();
            List<CaseRun> wins = subset.stream().filter(CaseRun::succeeded).toList();
            List<Integer> perRun = new ArrayList<>();
            for (int run = 1; run <= runs; run++) {
                int current = run;
                perRun.add((int) wins.stream().filter(r -> r.run() == current).count());
            }
            TreeSet<String> cases = new TreeSet<>();
            wins.forEach(r -> cases.add(r.caseId()));
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("rate", rateJson(rate(wins.size(), subset.size())));
            m.put("per_run", perRun);
            m.put("succeeding_cases", new ArrayList<>(cases));
            m.put("blocked", (int) subset.stream().filter(CaseRun::blocked).count());
            out.put(family.value(), m);
        }
        return out;
    }

    public static Map<String, Object> rateJson(Rate r) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("successes", r.successes());
        m.put("trials", r.trials());
        m.put("value", r.value());
        m.put("low", r.low());
        m.put("high", r.high());
        return m;
    }

    public static Map<String, Object> benignSummary(List<CaseRun> rows, double limit) {
        List<CaseRun> blocked = rows.stream().filter(CaseRun::blocked).toList();
        List<CaseRun> risky = rows.stream().filter(CaseRun::risky).toList();
        Map<String, Integer> cases = new TreeMap<>();
        blocked.forEach(r -> cases.merge(r.caseId(), 1, Integer::sum));
        Rate overall = rate(blocked.size(), rows.size());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("false_blocks", rateJson(overall));
        m.put("risky_false_blocks", rateJson(rate((int) risky.stream().filter(CaseRun::blocked).count(), risky.size())));
        m.put("blocked_cases", cases);
        m.put("unresolved_replies", (int) rows.stream().filter(r -> !r.unresolved().isEmpty()).count());
        m.put("within_limit", overall.value() <= limit);
        return m;
    }

    public static Map<String, Object> confusion(List<CaseRun> attacks, List<CaseRun> benign) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("attack_blocked_at_input", (int) attacks.stream().filter(r -> r.blocked() && r.stage().equals("input")).count());
        m.put("attack_allowed_by_input", (int) attacks.stream().filter(r -> !(r.blocked() && r.stage().equals("input"))).count());
        m.put("benign_blocked_at_input", (int) benign.stream().filter(r -> r.blocked() && r.stage().equals("input")).count());
        m.put("benign_allowed_by_input", (int) benign.stream().filter(r -> !(r.blocked() && r.stage().equals("input"))).count());
        return m;
    }
}
