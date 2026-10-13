package main
import "testing"
func TestCategory(t *testing.T) {
 cases := map[string]string{"x.PDF":"documents", "x.png":"images", "a.mp4":"videos", "x.zip":"archives", "test.xyz":"other"}
 for file, want := range cases { if got := category(file); got != want { t.Errorf("%s: got %s, want %s", file, got, want) } }
}
