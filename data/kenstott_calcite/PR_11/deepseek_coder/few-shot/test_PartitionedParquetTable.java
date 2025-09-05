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

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    
    @Test
    void testBasicAddition() {
        assertEquals(5, Calculator.add(2, 3));
        assertEquals(0, Calculator.add(-1, 1));
        assertEquals(0, Calculator.add(0, 0));
    }
    
    @Test
    void testEdgeCases() {
        assertEquals(3000000, Calculator.add(1000000, 2000000));
        assertEquals(-300, Calculator.add(-100, -200));
    }
    
    @Test
    void testZeroHandling() {
        assertEquals(5, Calculator.add(5, 0));
        assertEquals(5, Calculator.add(0, 5));
    }
}