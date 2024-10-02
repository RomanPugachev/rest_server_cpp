package com.example.simpleTaskTrackerWebApp.utils;

public class WordsGenerator {
    private static final String[] WORDS = new String[]{
            "apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon",
            "mango", "nectarine", "orange", "papaya", "quince", "raspberry", "strawberry", "tangerine", "watermelon", "xigua",
            "yellow", "zucchini", "avocado", "blueberry", "cranberry", "dragonfruit", "elderberry", "fig", "grapefruit", "honeydew",
            "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry", "strawberry", "tangerine", "watermelon", "xigua",
            "yellow", "zucchini", "avocado", "blueberry", "cranberry", "dragonfruit", "elderberry", "fig", "grapefruit", "honeydew",
            "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince",
            "raspberry", "strawberry", "tangerine", "watermelon", "xigua", "yellow", "zucchini", "avocado", "blueberry", "cranberry", "dragonfruit", "elderberry", "fig", "grapefruit", "honeydew",
            "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince"
    };

    public static String generateRandomWord() {
        int randomIndex = (int) (Math.random() * WORDS.length);
        return WORDS[randomIndex];
    }

    public static String generateRandomSentence(int wordCount) {
        StringBuilder sentence = new StringBuilder();
        for (int i = 0; i < wordCount; i++) {
            sentence.append(generateRandomWord()).append(" ");
        }
        return sentence.toString().trim();
    }

}
