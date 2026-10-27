package dev.plainround.guard.application;

/** Versioned prompt templates looked up by name such as assistant.v1. */
public interface PromptStore {
    String get(String name);
}
