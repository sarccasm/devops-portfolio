package main

import (
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

func category(name string) string {
	switch strings.ToLower(filepath.Ext(name)) {
	case ".txt", ".pdf", ".doc", ".docx", ".md":
		return "documents"
	case ".jpg", ".jpeg", ".png", ".gif", ".webp":
		return "images"
	case ".mp4", ".avi", ".mov", ".mkv":
		return "videos"
	case ".zip", ".tar", ".gz", ".7z", ".rar":
		return "archives"
	default:
		return "other"
	}
}

func sortFiles(dir string, dry bool) error {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return err
	}
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		src := filepath.Join(dir, e.Name())
		info, err := e.Info()
		if err != nil {
			return err
		}
		if !info.Mode().IsRegular() {
			continue
		}
		destDir := filepath.Join(dir, category(e.Name()))
		dest := filepath.Join(destDir, e.Name())
		if dry {
			fmt.Printf("WOULD MOVE %q -> %q\n", src, dest)
			continue
		}
		if err := os.MkdirAll(destDir, 0755); err != nil {
			return err
		}

		if _, err := os.Lstat(dest); err == nil {
			return fmt.Errorf("destination exists: %s", dest)
		} else if !os.IsNotExist(err) {
			return err
		}
		if err := os.Rename(src, dest); err != nil {

			if err := copyAndRemove(src, dest, info.Mode()); err != nil {
				return err
			}
		}
		fmt.Printf("MOVED %q -> %q\n", src, dest)
	}
	return nil
}

func copyAndRemove(src, dest string, perm os.FileMode) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()
	out, err := os.OpenFile(dest, os.O_WRONLY|os.O_CREATE|os.O_EXCL, perm)
	if err != nil {
		return err
	}
	_, err = io.Copy(out, in)
	if closeErr := out.Close(); err == nil {
		err = closeErr
	}
	if err != nil {
		os.Remove(dest)
		return err
	}
	return os.Remove(src)
}

func main() {
	fs := flag.NewFlagSet(os.Args[0], flag.ExitOnError)
	dry := fs.Bool("dry-run", false, "Print planned moves without modifying files")
	dir := fs.String("dir", "", "Directory to organize")
	fs.Usage = func() { fmt.Fprintf(os.Stderr, "Usage: %s -dir DIR [-dry-run]\n", os.Args[0]); fs.PrintDefaults() }
	if err := fs.Parse(os.Args[1:]); err != nil {
		os.Exit(2)
	}
	if *dir == "" || fs.NArg() != 0 {
		fs.Usage()
		os.Exit(2)
	}
	info, err := os.Stat(*dir)
	if err != nil || !info.IsDir() {
		fmt.Fprintln(os.Stderr, "Invalid directory")
		os.Exit(2)
	}
	if err := sortFiles(*dir, *dry); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
