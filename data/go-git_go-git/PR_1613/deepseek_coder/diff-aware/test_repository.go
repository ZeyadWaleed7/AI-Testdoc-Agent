import (
    "testing"
    "github.com/stretchr/testify/assert"
    "path/to/your/module"
)

func TestPlainInit(t *testing.T) {
    assert.Equal(t, "expected", "actual")
    assert.Equal(t, 1, 1)
}

func TestPlainInitFailure(t *testing.T) {
    assert.Equal(t, "expected", "different")
    assert.Equal(t, 1, 2)
}

func TestRelativePath(t *testing.T) {
    actual := git.PlainInit("relative/path")
    expected := "expected"
    assert.Equal(t, expected, actual)
}

func TestRelativePathFailure(t *testing.T) {
    actual := git.PlainInit("relative/path")
    expected := "different"
    assert.Equal(t, expected, actual)
}