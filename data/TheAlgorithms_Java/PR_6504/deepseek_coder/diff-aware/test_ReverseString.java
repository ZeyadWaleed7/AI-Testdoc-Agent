import java.util.Stack;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class ReverseStringTest {

    @BeforeEach
    public void setup() {
        // Setup code here if any
    }

    @AfterEach
    public void teardown() {
        // Teardown code here if any
    }

    @Test
    public void testReverseStringUsingStackWithNormalCases() {
        assertEquals("dlroW olleH", ReverseString.reverseStringUsingStack("Hello World"));
        assertEquals("dlrowolleh", ReverseString.reverseStringUsingStack("helloworld"));
        assertEquals("987654321", ReverseString.reverseStringUsingStack("123456789"));
        assertEquals("zyx CBA 321!", ReverseString.reverseStringUsingStack("!zyx CBA 321"));
        assertEquals("A", ReverseString.reverseStringUsingStack("A"));
        assertEquals("!123 ABC xyz!", ReverseString.reverseStringUsingStack("!123 ABC xyz!"));
    }

    @ParameterizedTest
    @CsvSource({"'Hello World', 'dlroW olleH'", "'helloworld', 'dlrowolleh'", "'123456789', '987654321'", "''', ''", "'A', 'A'", "!'123 ABC xyz!', '!zyx CBA 321!'", "'Abc 123 Xyz', 'zyX 321 cbA'", "'12.34,56;78:90', '09:87;65,43.21'", "'abcdEFGHiJKL', 'LKJiHGFEdcba'", "'MixOf123AndText!', '!txeTdnA321fOxiM'"})
    public void testReverseStringUsingStackWithEdgeCases(String input, String expectedOutput) {
        assertEquals(expectedOutput, ReverseString.reverseStringUsingStack(input));
    }

    @Test
    public void testReverseStringUsingStackWithNullInput() {
        assertThrows(IllegalArgumentException.class, () -> ReverseString.reverseStringUsingStack(null));
    }

    @ParameterizedTest
    @CsvSource({"'Hello World', 'dlroW olleH'", "'helloworld', 'dlrowolleh'", "'123456789', '987654321'", "''', ''", "'A', 'A'", "!'123 ABC xyz!', '!zyx CBA 321!'", "'Abc 123 Xyz', 'zyX 321 cbA'", "'12.34,56;78:90', '09:87;65,43.21'", "'abcdEFGHiJKL', 'LKJiHGFEdcba'", "'MixOf123AndText!', '!txeTdnA321fOxiM'"})
    public void testReverseStringUsingRecursion(String input, String expectedOutput) {
        assertEquals(expectedOutput, ReverseString.reverseStringUsingRecursion(input));
    }
}