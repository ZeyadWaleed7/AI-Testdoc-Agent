import org.apache.calcite.adapter.file.execution.ExecutionEngineConfig;
import org.apache.calcite.adapter.file.partition.PartitionDetector;
import org.apache.calcite.adapter.file.partition.PartitionedTableConfig;
import org.apache.calcite.DataContext;
import org.apache.calcite.adapter.java.JavaTypeFactory;
import org.apache.calcite.linq4j.AbstractEnumerable;
import org.apache.calcite.linq4j.Enumerable;
import org.apache.calcite.linq4j.Enumerator;
import org.apache.calcite.rel.type.RelDataType;
import org.apache.calcite.rel.type.RelDataTypeFactory;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class PartitionedParquetTableTest {

    private PartitionedParquetTable partitionedParquetTable;

    @BeforeEach
    void setUp() {
        partitionedParquetTable = new PartitionedParquetTable();
    }

    @Test
    void testCreateTable() {
        assertTrue(partitionedParquetTable.createTable());
    }

    @Test
    void testInsertData() {
        assertTrue(partitionedParquetTable.insertData());
    }

    @Test
    void testQueryData() {
        assertTrue(partitionedParquetTable.queryData());
    }
}