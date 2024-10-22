package com.example.simpleTaskTrackerWebApp.utils;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.BeforeEach;

class StringGeneratorTest {

    private StringGenerator stringGenerator;

    @BeforeEach
    void setUp() {
        stringGenerator = new StringGenerator();
    }

    @Test
    void testGenerateRandomStringLength() {
        int expectedLength = 10;
        String result = stringGenerator.generateRandomString(expectedLength);
        assertEquals(expectedLength, result.length());
    }

    @Test
    void testGenerateRandomStringZeroLength() {
        String result = stringGenerator.generateRandomString(0);
        assertTrue(result.isEmpty());
    }

    @Test
    void testGenerateRandomStringNegativeLength() {
        String result = stringGenerator.generateRandomString(-5);
        assertTrue(result.isEmpty());
    }

    @Test
    void testGenerateRandomStringUniqueness() {
        String result1 = stringGenerator.generateRandomString(20);
        String result2 = stringGenerator.generateRandomString(20);
        assertNotEquals(result1, result2);
    }

    @Test
    void testGenerateRandomStringLargeLength() {
        int largeLength = 10000;
        String result = stringGenerator.generateRandomString(largeLength);
        assertEquals(largeLength, result.length());
    }
}
