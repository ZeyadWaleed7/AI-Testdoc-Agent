import java.util.Stack;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class ReverseStringTest {
    
    @Test
    void testNormalCases() {
        assertEquals("abc", ReverseString.reverse("cba"));
        assertEquals("a", ReverseString.reverse("a"));
        assertEquals("1234567890", ReverseString.reverse("0987654321"));
    }
    
    @Test
    void testEdgeCases() {
        assertEquals("", ReverseString.reverse(""));
        assertEquals("a", ReverseString.reverse("a"));
        assertEquals("zyxwvutsrqponmlkjihgfedcba", ReverseString.reverse("abcdefghijklmnopqrstuvwxyz"));
    }
    
    @Test
    void testNullHandling() {
        assertNull(ReverseString.reverse(null));
    }
    
    @Test
    void testEmptyString() {
        assertEquals("", ReverseString.reverse(""));
    }
}