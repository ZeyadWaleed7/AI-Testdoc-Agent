import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.calcite.adapter.file.FileSchema;
import org.apache.calcite.adapter.file.converters.FileConversionManager;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;

import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class ConversionMetadataTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(ConversionMetadata.class);
    private static final String METADATA_FILE = ".conversions.json";
    private static final ObjectMapper MAPPER = new ObjectMapper()
            .enable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);

    @Test
    void testNormalCases() throws Exception {
        Map<String, String> expectedMetadata = new HashMap<>();
        expectedMetadata.put("key1", "value1");
        expectedMetadata.put("key2", "value2");

        try (MockedStatic<Files> mockedFiles = Mockito.mockStatic(Files.class)) {
            mockedFiles.when(Files::readAllLines).thenReturn(new String[]{"key1=value1", "key2=value2"});

            Map<String, String> actualMetadata = ConversionMetadata.loadMetadata(METADATA_FILE);

            assertEquals(expectedMetadata, actualMetadata);
        }
    }

    @Test
    void testEdgeCases() throws Exception {
        Map<String, String> expectedMetadata = new HashMap<>();
        expectedMetadata.put("key1", "value1");
        expectedMetadata.put("key2", "value2");

        try (MockedStatic<Files> mockedFiles = Mockito.mockStatic(Files.class)) {
            mockedFiles.when(Files::readAllLines).thenReturn(new String[]{"key1=value1", "key2=value2", "key3=value3"});

            Map<String, String> actualMetadata = ConversionMetadata.loadMetadata(METADATA_FILE);

            assertEquals(expectedMetadata, actualMetadata);
        }
    }

    @Test
    void testErrorHandling() throws Exception {
        try (MockedStatic<Files> mockedFiles = Mockito.mockStatic(Files.class)) {
            mockedFiles.when(Files::readAllLines).thenThrow(new IOException("Test Error"));

            assertThrows(IOException.class, () -> ConversionMetadata.loadMetadata(METADATA_FILE));
        }
    }
}