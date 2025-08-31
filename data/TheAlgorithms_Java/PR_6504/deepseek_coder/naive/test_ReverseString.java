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
        assertEquals("abc", reverseString.reverseString("cba"));
        assertEquals("12345", reverseString.reverseString("54321"));
        assertEquals("a", reverseString.reverseString("a"));
    }

    @Test
    void testReverseString_edgeCases() {
        assertEquals("", reverseString.reverseString(""));
        assertEquals("A", reverseString.reverseString("A"));
        assertEquals("Z", reverseString.reverseString("Z"));
    }

    @Test
    void testReverseString_errorConditions() {
        assertThrows(IllegalArgumentException.class, () -> reverseString.reverseString(null));
        assertThrows(IllegalArgumentException.class, () -> reverseString.reverseString(" "));
    }

    @AfterEach
    void tearDown() {
        reverseString = null;
    }
}