#!/usr/bin/env python3
"""
Test script to verify language detection functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agent.language_detector import LanguageDetector

def test_language_detection():
    """Test the language detection system."""
    
    print("🧪 Testing Language Detection System")
    print("=" * 50)
    
    # Test file extension detection
    test_files = [
        "test.py",
        "main.js",
        "app.ts",
        "Calculator.java",
        "vector.cpp",
        "utils.c",
        "service.cs",
        "handler.go",
        "parser.rs",
        "helper.php",
        "model.rb",
        "view.swift",
        "data.kt",
        "logic.scala",
        "app.dart",
        "analysis.r",
        "algorithm.m",
        "script.pl",
        "config.sh",
        "module.ps1",
        "query.sql",
        "page.html",
        "style.css",
        "config.yml",
        "data.json",
        "schema.xml",
        "README.md",
        "Dockerfile",
        "Makefile",
        "CMakeLists.txt",
        "build.gradle",
        "pom.xml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "requirements.txt"
    ]
    
    print("\n📁 File Extension Detection:")
    for test_file in test_files:
        detected_lang = LanguageDetector.detect_language_from_file(test_file)
        status = "✅" if detected_lang else "❌"
        print(f"  {status} {test_file:25} -> {detected_lang or 'Unknown'}")
    
    # Test content-based detection
    print("\n📝 Content-Based Detection:")
    
    test_contents = [
        ("def hello_world():", "python"),
        ("function greet() {", "javascript"),
        ("public class Test {", "java"),
        ("int main() {", "cpp"),
        ("func process() {", "go"),
        ("fn calculate() {", "rust"),
        ("public function test() {", "php"),
        ("def process_data", "ruby"),
        ("class ViewController {", "swift"),
        ("fun process() {", "kotlin"),
        ("def process():", "scala"),
        ("#!/bin/bash", "bash"),
        ("#!/usr/bin/perl", "perl"),
        ("#!/usr/bin/ruby", "ruby"),
        ("<!DOCTYPE html>", "html"),
        ("<?xml version=\"1.0\"?>", "xml"),
        ("{\"key\": \"value\"}", "json"),
        ("---\nkey: value", "yaml"),
        ("# Header\n\nContent", "markdown")
    ]
    
    for content, expected_lang in test_contents:
        detected_lang = LanguageDetector.detect_language_from_content(content)
        status = "✅" if detected_lang == expected_lang else "❌"
        print(f"  {status} {content:25} -> {detected_lang or 'Unknown'} (expected: {expected_lang})")
    
    # Test function patterns
    print("\n🔍 Function Pattern Detection:")
    languages_to_test = ["python", "javascript", "java", "cpp", "go", "rust"]
    
    for lang in languages_to_test:
        patterns = LanguageDetector.get_function_patterns_for_language(lang)
        test_frameworks = LanguageDetector.get_test_frameworks_for_language(lang)
        print(f"  📚 {lang:12}: {len(patterns)} patterns, {len(test_frameworks)} test frameworks")
        print(f"      Frameworks: {', '.join(test_frameworks[:3])}{'...' if len(test_frameworks) > 3 else ''}")
    
    # Test supported languages
    print("\n🌍 Supported Languages:")
    supported = LanguageDetector.get_supported_languages()
    print(f"  Total: {len(supported)} languages")
    print(f"  Languages: {', '.join(sorted(supported))}")
    
    print("\n🎉 Language Detection Test Complete!")

if __name__ == "__main__":
    test_language_detection()
