import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.calcite.adapter.file.FileSchema;
import org.apache.calcite.adapter.file.converters.FileConversionManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

import java.io.File;
import java.io.IOException;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

class ConversionMetadataTest {
    private static final String METADATA_FILE = ".conversions.json";
    private static final String TEST_JSON = "{\"testKey\":\"testValue\"}";
    private ConversionMetadata conversionMetadata;
    private MockedStatic<ConversionMetadata> mocked;

    @BeforeEach
    void setUp() {
        conversionMetadata = new ConversionMetadata();
        mocked = Mockito.mockStatic(ConversionMetadata.class);
    }

    @Test
    void testReadMetadata() throws IOException {
        // Given
        when(mocked.readMetadataFile(METADATA_FILE)).thenReturn(TEST_JSON);

        // When
        String result = conversionMetadata.readMetadataFile(METADATA_FILE);

        // Then
        assertEquals(TEST_JSON, result);
    }

    @Test
    void testParseMetadata() {
        // Given
        when(mocked.parseMetadata(TEST_JSON)).thenReturn(new ConversionMetadata());

        // When
        ConversionMetadata result = conversionMetadata.parseMetadata(TEST_JSON);

        // Then
        assertEquals(new ConversionMetadata(), result);
    }
}