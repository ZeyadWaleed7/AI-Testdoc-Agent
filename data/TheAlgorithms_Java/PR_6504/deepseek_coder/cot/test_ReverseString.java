import java.util.Stack;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ReverseStringTest {

    private ReverseString reverseString;

    @BeforeEach
    void setUp() {
        reverseString = new ReverseString();
    }

    @Test
    void testReverseString_normalCases() {
        String input = "abcde";
        String expectedOutput = "edcba";
        assertEquals(expectedOutput, reverseString.reverseString(input));
    }

    @Test
    void testReverseString_edgeCases() {
        String input = "";
        String expectedOutput = "";
        assertEquals(expectedOutput, reverseString.reverseString(input));

        input = "a";
        expectedOutput = "a";
        assertEquals(expectedOutput, reverseString.reverseString(input));
    }

    @Test
    void testReverseString_errorConditions() {
        assertThrows(NullPointerException.class, () -> reverseString.reverseString(null));
    }

    @AfterEach
    void tearDown() {
        reverseString = null;
    }
}