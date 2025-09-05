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