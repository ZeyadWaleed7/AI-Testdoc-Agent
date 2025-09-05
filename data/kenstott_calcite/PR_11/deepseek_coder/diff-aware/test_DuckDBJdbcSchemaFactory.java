import org.apache.calcite.adapter.jdbc.JdbcSchema;
import org.apache.calcite.adapter.jdbc.JdbcConvention;
import org.apache.calcite.adapter.file.format.parquet.ParquetConversionUtil;
import org.apache.calcite.adapter.file.metadata.ConversionMetadata;
import org.apache.calcite.avatica.util.Casing;
import org.apache.calcite.config.Lex;
import org.apache.calcite.config.NullCollation;
import org.apache.calcite.linq4j.tree.Expression;
import org.apache.calcite.schema.Schemas;
import org.apache.calcite.schema.SchemaPlus;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DuckDBJdbcSchemaFactoryTest {

    private DuckDBJdbcSchemaFactory schemaFactory;

    @BeforeEach
    void setUp() {
        schemaFactory = new DuckDBJdbcSchemaFactory();
    }

    @Test
    void testCreateSchema() {
        assertDoesNotThrow(() -> schemaFactory.createSchema("test_schema"));
    }

    @Test
    void testCreateTable() {
        assertDoesNotThrow(() -> schemaFactory.createTable("test_schema", "test_table", "id INT PRIMARY KEY"));
    }

    @Test
    void testInsertData() {
        assertDoesNotThrow(() -> schemaFactory.insertData("test_schema", "test_table", "id", 1));
    }

    @Test
    void testSelectData() {
        assertDoesNotThrow(() -> schemaFactory.selectData("test_schema", "test_table", "id", 1));
    }
}