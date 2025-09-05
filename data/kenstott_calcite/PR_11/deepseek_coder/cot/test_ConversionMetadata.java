import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.apache.calcite.adapter.file.FileSchema;
import org.apache.calcite.adapter.file.converters.FileConversionManager;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.File;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.channels.FileChannel;

import org.junit.jupiter.api.*;
import org.mockito.*;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ConversionMetadataTest {

    @InjectMocks private ConversionMetadata conversionMetadata;

    @Test
    void testReadMetadata_Success() {
        // Setup
        String metadataFile = ".conversions.json";
        ObjectMapper mockMapper = Mockito.mock(ObjectMapper.class);
        ConversionMetadata metadata = new ConversionMetadata(metadataFile, mockMapper);

        // Expected behavior
        when(mockMapper.readValue(metadataFile, ConversionMetadata.class)).thenReturn(new ConversionMetadata());

        // Act
        ConversionMetadata result = metadata.readMetadata();

        // Assert
        assertNotNull(result);
    }

    @Test
    void testReadMetadata_Failure() {
        // Setup
        String metadataFile = ".conversions.json";
        ObjectMapper mockMapper = Mockito.mock(ObjectMapper.class);
        ConversionMetadata metadata = new ConversionMetadata(metadataFile, mockMapper);

        // Expected behavior
        when(mockMapper.readValue(metadataFile, ConversionMetadata.class)).thenThrow(new RuntimeException());

        // Act and Assert
        assertThrows(RuntimeException.class, () -> metadata.readMetadata());
    }
}