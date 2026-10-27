package dev.plainround.guard.infrastructure;

import dev.plainround.guard.application.OrderLookup;
import dev.plainround.guard.domain.Shop;
import dev.plainround.guard.domain.Shop.AttackCase;
import dev.plainround.guard.domain.Shop.BenignCase;
import dev.plainround.guard.domain.Shop.Customer;
import dev.plainround.guard.domain.Shop.Family;
import dev.plainround.guard.domain.Shop.Order;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Reads the same suites and shop data as the Python port, and is the read-only order lookup. */
public final class DataFiles implements OrderLookup {

    private static final JsonMapper JSON = JsonMapper.builder().build();

    private final Map<String, Order> orders = new LinkedHashMap<>();
    private final Map<String, Customer> customers = new LinkedHashMap<>();

    public DataFiles(Path dataDir) {
        for (JsonNode r : lines(dataDir.resolve("customers.jsonl"))) {
            customers.put(r.get("customer_id").asString(), new Customer(r.get("customer_id").asString(), r.get("name").asString(), r.get("email").asString(), r.get("phone").asString()));
        }
        for (JsonNode r : lines(dataDir.resolve("orders.jsonl"))) {
            List<String> items = new ArrayList<>();
            r.get("items").forEach(i -> items.add(i.asString()));
            orders.put(r.get("order_id").asString(), new Order(r.get("order_id").asString(), r.get("customer_id").asString(), r.get("status").asString(),
                    items, r.get("total_cents").asInt(), r.get("ship_to").asString(), r.get("tracking").asString(), r.get("note").asString()));
        }
    }

    static List<JsonNode> lines(Path file) {
        try {
            List<JsonNode> rows = new ArrayList<>();
            for (String line : Files.readAllLines(file, StandardCharsets.UTF_8)) {
                if (!line.isBlank()) {
                    rows.add(JSON.readTree(line));
                }
            }
            return rows;
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public String find(String orderId, String note) {
        Order order = orders.get(orderId);
        return order == null ? null : Shop.renderRecord(order, customers.get(order.customerId()), note);
    }

    public Iterable<String> forbiddenFor(String customerId) {
        Set<String> values = new LinkedHashSet<>();
        for (Customer c : customers.values()) {
            if (!c.customerId().equals(customerId)) {
                values.add(c.email());
                values.add(c.phone());
            }
        }
        for (Order o : orders.values()) {
            if (!o.customerId().equals(customerId)) {
                values.add(o.orderId());
                values.add(o.tracking());
            }
        }
        return values;
    }

    public List<String> ownValues(String customerId) {
        Customer c = customers.get(customerId);
        return List.of(c.email(), c.phone());
    }

    public static List<AttackCase> loadAttacks(Path dataDir) {
        List<AttackCase> cases = new ArrayList<>();
        for (JsonNode r : lines(dataDir.resolve("attacks.jsonl"))) {
            JsonNode override = r.get("note_override");
            List<String> leaks = new ArrayList<>();
            if (r.has("leak_values")) {
                r.get("leak_values").forEach(v -> leaks.add(v.asString()));
            }
            cases.add(new AttackCase(r.get("case_id").asString(), Family.of(r.get("family").asString()), r.get("customer").asString(), r.get("message").asString(),
                    override == null ? null : override.get("order_id").asString(), override == null ? null : override.get("note").asString(),
                    r.has("help_page") ? r.get("help_page").asString() : null, leaks));
        }
        return cases;
    }

    public static List<BenignCase> loadBenign(Path dataDir) {
        List<BenignCase> cases = new ArrayList<>();
        for (JsonNode r : lines(dataDir.resolve("benign.jsonl"))) {
            cases.add(new BenignCase(r.get("case_id").asString(), r.get("customer").asString(), r.get("message").asString(), r.get("risky").asBoolean()));
        }
        return cases;
    }

    public static String loadCanary(Path dataDir) {
        try {
            return Files.readString(dataDir.resolve("canary.txt"), StandardCharsets.UTF_8).strip();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public static double loadLimit(Path evalsDir) {
        try {
            return JSON.readTree(Files.readString(evalsDir.resolve("limits.json"), StandardCharsets.UTF_8)).get("false_block_limit").asDouble();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
