import org.apache.calcite.adapter.file.converters.DocxTableScanner;
import org.apache.calcite.adapter.file.converters.FileConversionManager;
import org.apache.calcite.adapter.file.converters.MarkdownTableScanner;
import org.apache.calcite.adapter.file.converters.PptxTableScanner;
import org.apache.calcite.adapter.file.converters.SafeExcelToJsonConverter;
import org.apache.calcite.adapter.file.execution.ExecutionEngineConfig;
import org.apache.calcite.adapter.file.metadata.ConversionMetadata;
import org.apache.calcite.adapter.file.storage.cache.StorageCacheManager;
import org.apache.calcite.adapter.file.format.csv.CsvTypeInferrer;
import org.apache.calcite.adapter.file.format.json.JsonMultiTableFactory;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FileSchemaTest {
    private FileSchema fileSchema;

    @BeforeEach
    void setUp() {
        fileSchema = new FileSchema();
    }

    @Test
    void testSetAndGetName() {
        String testName = "testName";
        fileSchema.setName(testName);
        assertEquals(testName, fileSchema.getName());
    }

    @Test
    void testSetAndGetPath() {
        String testPath = "/test/path";
        fileSchema.setPath(testPath);
        assertEquals(testPath, fileSchema.getPath());
    }

    @Test
    void testSetAndGetSize() {
        long testSize = 1024L;
        fileSchema.setSize(testSize);
        assertEquals(testSize, fileSchema.getSize());
    }

    @Test
    void testSetAndGetCreationTime() {
        long testCreationTime = 1609459200L; // 2021-01-01 00:00:00
        fileSchema.setCreationTime(testCreationTime);
        assertEquals(testCreationTime, fileSchema.getCreationTime());
    }

    @Test
    void testSetAndGetModificationTime() {
        long testModificationTime = 1612592000L; // 2021-01-02 00:00:00
        fileSchema.setModificationTime(testModificationTime);
        assertEquals(testModificationTime, fileSchema.getModificationTime());
    }
}