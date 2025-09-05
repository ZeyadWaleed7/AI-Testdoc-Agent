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

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest  {
    
    @Test
    void testBasicAddition()  {
        assertEquals(5, Calculator.add(2, 3));
        assertEquals(0, Calculator.add(-1, 1));
        assertEquals(0, Calculator.add(0, 0));
    }
    
    @Test
    void testEdgeCases()  {
        assertEquals(3000000, Calculator.add(1000000, 2000000));
        assertEquals(-300, Calculator.add(-100, -200));
    }
    
    @Test
    void testZeroHandling()  {
        assertEquals(5, Calculator.add(5, 0));
        assertEquals(5, Calculator.add(0, 5));
    }
}