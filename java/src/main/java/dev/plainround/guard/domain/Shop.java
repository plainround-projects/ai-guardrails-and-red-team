package dev.plainround.guard.domain;

import java.util.List;

/** The sample shop, cases and the redaction, rules and output checks (ports of shop.py, cases.py, redaction.py, rules.py, output_checks.py, effects.py). */
public final class Shop {

    private Shop() {}

    public record Customer(String customerId, String name, String email, String phone) {}

    public record Order(String orderId, String customerId, String status, List<String> items, int totalCents, String shipTo, String tracking, String note) {}

    public static String renderRecord(Order order, Customer customer, String note) {
        String total = String.format("$%d.%02d", order.totalCents() / 100, order.totalCents() % 100);
        String shown = note == null ? order.note() : note;
        return "Order " + order.orderId() + " | customer: " + customer.customerId() + " | email: " + customer.email() + " | status: "
                + order.status() + " | items: " + String.join(", ", order.items()) + " | total: " + total + " | ship to: " + order.shipTo()
                + " | tracking: " + order.tracking() + " | note: " + (shown == null || shown.isEmpty() ? "none" : shown);
    }

    public enum Family {
        DIRECT("direct_injection"),
        INDIRECT("indirect_injection"),
        ROLEPLAY("roleplay"),
        CROSS("cross_customer"),
        EXTRACTION("prompt_extraction");

        private final String value;

        Family(String value) {
            this.value = value;
        }

        public String value() {
            return value;
        }

        public static Family of(String value) {
            for (Family f : values()) {
                if (f.value.equals(value)) {
                    return f;
                }
            }
            throw new IllegalArgumentException("unknown family " + value);
        }
    }

    public record AttackCase(String caseId, Family family, String customer, String message, String noteOrder, String note, String helpPage, List<String> leakValues) {}

    public record BenignCase(String caseId, String customer, String message, boolean risky) {}
}
