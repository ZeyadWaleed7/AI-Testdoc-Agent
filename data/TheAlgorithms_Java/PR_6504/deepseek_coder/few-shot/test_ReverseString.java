import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

import java.util.Stack;

import static org.junit.jupiter.api.Assertions.*;

class ReverseStringTest {

    @Test
    void testReverseString_normalCase(MockedStatic<String> mockedStatic) {
        String input = "hello";
        String expectedOutput = "olleh";
        mockedStatic.when(ReverseString.reverseString(input)).thenReturn(expectedOutput);
        assertEquals(expectedOutput, ReverseString.reverseString(input));
    }

    @Test
    void testReverseString_edgeCase(MockedStatic<String> mockedStatic) {
        String input = "";
        String expectedOutput = "";
        mockedStatic.when(ReverseString.reverseString(input)).thenReturn(expectedOutput);
        assertEquals(expectedOutput, ReverseString.reverseString(input));
    }

    @Test
    void testReverseString_errorCase(MockedStatic<String> mockedStatic) {
        String input = null;
        assertThrows(NullPointerException.class, () -> ReverseString.reverseString(input));
    }
}