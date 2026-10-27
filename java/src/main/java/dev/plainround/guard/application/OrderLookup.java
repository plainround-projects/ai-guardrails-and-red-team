package dev.plainround.guard.application;

/** The read-only find_order tool. */
public interface OrderLookup {
    /** The rendered record of any order (the note may be replaced for this call), or null. */
    String find(String orderId, String note);
}
