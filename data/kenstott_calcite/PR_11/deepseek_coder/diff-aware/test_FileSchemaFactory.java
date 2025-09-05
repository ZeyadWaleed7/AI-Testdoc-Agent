import org.apache.calcite.adapter.file.duckdb.DuckDBJdbcSchemaFactory;
import org.apache.calcite.adapter.file.execution.ExecutionEngineConfig;
import org.apache.calcite.adapter.file.execution.duckdb.DuckDBConfig;
import org.apache.calcite.adapter.file.metadata.InformationSchema;
import org.apache.calcite.adapter.file.metadata.PostgresMetadataSchema;
import org.apache.calcite.adapter.jdbc.JdbcSchema;
import org.apache.calcite.model.ModelHandler;
import org.apache.calcite.schema.Schema;
import org.apache.calcite.schema.SchemaFactory;
import org.apache.calcite.schema.SchemaPlus;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FileSchemaFactoryTest {
    private FileSchemaFactory fileSchemaFactory;

    @BeforeEach
    void setUp() {
        fileSchemaFactory = new FileSchemaFactory();
    }

    @Test
    void testCreateFileSchema() {
        // Given
        String fileName = "test.txt";
        String content = "This is a test content";

        // When
        FileSchema fileSchema = fileSchemaFactory.createFileSchema(fileName, content);

        // Then
        assertEquals(fileName, fileSchema.getFileName());
        assertEquals(content, fileSchema.getContent());
    }
}