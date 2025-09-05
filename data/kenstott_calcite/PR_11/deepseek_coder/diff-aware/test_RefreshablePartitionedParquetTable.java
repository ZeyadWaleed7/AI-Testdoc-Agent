import org.apache.calcite.adapter.file.execution.ExecutionEngineConfig;
import org.apache.calcite.adapter.file.partition.PartitionDetector;
import org.apache.calcite.adapter.file.partition.PartitionedTableConfig;
import org.apache.calcite.adapter.file.table.PartitionedParquetTable;
import org.apache.calcite.DataContext;
import org.apache.calcite.linq4j.Enumerable;
import org.apache.calcite.rel.type.RelDataType;
import org.apache.calcite.rel.type.RelDataTypeFactory;
import org.apache.calcite.schema.ScannableTable;
import org.apache.calcite.schema.impl.AbstractTable;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

public class RefreshablePartitionedParquetTableTest {

    @Mock
    private AbstractTable mockTable;

    @BeforeEach
    public void setup() {
        MockitoAnnotations.initMocks(this);
        when(mockTable.refresh()).thenReturn(true);
    }

    @Test
    public void testRefresh() {
        // Given
        RefreshablePartitionedParquetTable table = new RefreshablePartitionedParquetTable();

        // When
        boolean result = table.refresh();

        // Then
        assertTrue(result);
    }

    @Test
    public void testScan() {
        // Given
        RefreshablePartitionedParquetTable table = new RefreshablePartitionedParquetTable();
        List<String> expectedResult = List.of("test1", "test2", "test3");

        // When
        when(mockTable.scan()).thenReturn(expectedResult);
        List<String> result = table.scan();

        // Then
        assertTrue(result.equals(expectedResult));
    }
}