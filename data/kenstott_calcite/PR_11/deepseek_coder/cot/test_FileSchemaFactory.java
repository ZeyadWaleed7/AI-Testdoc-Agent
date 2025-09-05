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
    void testCreateSchema_normalCase() {
        // Given
        String filePath = "test.db";
        String schemaName = "testSchema";

        // When
        Schema schema = fileSchemaFactory.createSchema(filePath, schemaName);

        // Then
        assertNotNull(schema);
        assertEquals(schemaName, schema.getName());
    }

    @Test
    void testCreateSchema_edgeCase() {
        // Given
        String filePath = "";
        String schemaName = null;

        // When
        Schema schema = fileSchemaFactory.createSchema(filePath, schemaName);

        // Then
        assertThrows(IllegalArgumentException.class, () -> schema.getName());
    }

    @Test
    void testCreateSchema_errorCondition() {
        // Given
        String filePath = null;
        String schemaName = "";

        // When
        Throwable exception = catchThrowable(() -> fileSchemaFactory.createSchema(filePath, schemaName));

        // Then
        assertTrue(exception instanceof IllegalArgumentException);
    }
}