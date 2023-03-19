import os
import re
import tempfile
from typing import List
import unittest
from src.code_snippet_extractor import ChunkCodeSnippet, CodeSnippet

from src.cxx_code_snippet_extractor import CXXCodeSnippetExtractor


class TestCXXCodeSnippetExtractor(unittest.TestCase):

    __tmp_dir: tempfile.TemporaryDirectory
    __cxx_code_snippet_extractor: CXXCodeSnippetExtractor

    @classmethod
    def setUpClass(self):
        self.__tmp_dir = tempfile.TemporaryDirectory("gpt_code_gen_test")
        self.__cxx_code_snippet_extractor = CXXCodeSnippetExtractor()

    @classmethod
    def tearDownClass(self):
        self.__tmp_dir.cleanup()

    def test_extract_struct_with_functions(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
struct VideoFormat {
  OPTIONAL_ENUM_SIZE_T {
    
    kMaxWidthInPixels = 3840,
    
    kMaxHeightInPixels = 2160,
    
    kMaxFps = 60,
  };
  
  int width;   
  
  int height;  
  
  int fps;
  
  void SetAll(const VideoFormat& change) {
      SET_FROM(width);
      SET_FROM(height);
  }

  bool operator<(const VideoFormat& fmt) const {
    if (height != fmt.height) {
      return height < fmt.height;
    } else if (width != fmt.width) {
      return width < fmt.width;
    } else {
      return fps < fmt.fps;
    }
  }
  bool operator==(const VideoFormat& fmt) const {
    return width == fmt.width && height == fmt.height && fps == fmt.fps;
  }
  bool operator!=(const VideoFormat& fmt) const {
    return !operator==(fmt);
  }
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        expect_content = """
struct VideoFormat {
  OPTIONAL_ENUM_SIZE_T {
    kMaxWidthInPixels = 3840,
    kMaxHeightInPixels = 2160,
    kMaxFps = 60,
  };
  int width;   
  int height;  
  int fps;
};
""".strip("\n")

        code_snippet = code_snippet_files[0].code_snippets[0]

        self.assertEqual(expect_content, code_snippet.source)

    def test_extract_struct_with_constructors(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
struct ScreenCaptureParameters {
  
  VideoDimensions dimensions;
  
  int frameRate;
  
  int bitrate;
  
  bool captureMouseCursor;
  
  bool windowFocus;
  
  view_t *excludeWindowList;
  
  int excludeWindowCount;

  int highLightWidth;
  
  unsigned int highLightColor;
  
  bool enableHighLight;

  ScreenCaptureParameters()
    : dimensions(1920, 1080), frameRate(5), bitrate(STANDARD_BITRATE), captureMouseCursor(true), windowFocus(false), excludeWindowList(OPTIONAL_NULLPTR), excludeWindowCount(0), highLightWidth(0), highLightColor(0), enableHighLight(false)  {}
  ScreenCaptureParameters(const VideoDimensions& d, int f, int b)
    : dimensions(d),
      frameRate(f),
      bitrate(b),
      captureMouseCursor(true),
      windowFocus(false),
      excludeWindowList(OPTIONAL_NULLPTR),
      excludeWindowCount(0),
      highLightWidth(0),
      highLightColor(0),
      enableHighLight(false) {}
  ScreenCaptureParameters(int width, int height, int f, int b)
    : dimensions(width, height), frameRate(f), bitrate(b), captureMouseCursor(true), windowFocus(false), excludeWindowList(OPTIONAL_NULLPTR), excludeWindowCount(0), highLightWidth(0), highLightColor(0), enableHighLight(false){}
  ScreenCaptureParameters(int width, int height, int f, int b, bool cur, bool fcs)
    : dimensions(width, height), frameRate(f), bitrate(b), captureMouseCursor(cur), windowFocus(fcs), excludeWindowList(OPTIONAL_NULLPTR), excludeWindowCount(0), highLightWidth(0), highLightColor(0), enableHighLight(false) {}
  ScreenCaptureParameters(int width, int height, int f, int b, view_t *ex, int cnt)
    : dimensions(width, height), frameRate(f), bitrate(b), captureMouseCursor(true), windowFocus(false), excludeWindowList(ex), excludeWindowCount(cnt), highLightWidth(0), highLightColor(0), enableHighLight(false) {}
  ScreenCaptureParameters(int width, int height, int f, int b, bool cur, bool fcs, view_t *ex, int cnt)
    : dimensions(width, height), frameRate(f), bitrate(b), captureMouseCursor(cur), windowFocus(fcs), excludeWindowList(ex), excludeWindowCount(cnt), highLightWidth(0), highLightColor(0), enableHighLight(false) {}
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        expect_content = """
struct ScreenCaptureParameters {
  VideoDimensions dimensions;
  int frameRate;
  int bitrate;
  bool captureMouseCursor;
  bool windowFocus;
  view_t *excludeWindowList;
  int excludeWindowCount;
  int highLightWidth;
  unsigned int highLightColor;
  bool enableHighLight;
};
""".strip("\n")

        code_snippet = code_snippet_files[0].code_snippets[0]

        self.assertEqual(expect_content, code_snippet.source)

    def test_extract_struct_with_constructors_and_functions(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
struct VideoFormat {
  OPTIONAL_ENUM_SIZE_T {
    
    kMaxWidthInPixels = 3840,
    
    kMaxHeightInPixels = 2160,
    
    kMaxFps = 60,
  };
  
  int width;   
  
  int height;  
  
  int fps;
  VideoFormat() : width(FRAME_WIDTH_640), height(FRAME_HEIGHT_360), fps(FRAME_RATE_FPS_15) {}
  VideoFormat(int w, int h, int f) : width(w), height(h), fps(f) {}
  ~VideoFormat() {}

  bool operator<(const VideoFormat& fmt) const {
    if (height != fmt.height) {
      return height < fmt.height;
    } else if (width != fmt.width) {
      return width < fmt.width;
    } else {
      return fps < fmt.fps;
    }
  }
  bool operator==(const VideoFormat& fmt) const {
    return width == fmt.width && height == fmt.height && fps == fmt.fps;
  }
  bool operator!=(const VideoFormat& fmt) const {
    return !operator==(fmt);
  }
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        expect_content = """
struct VideoFormat {
  OPTIONAL_ENUM_SIZE_T {
    kMaxWidthInPixels = 3840,
    kMaxHeightInPixels = 2160,
    kMaxFps = 60,
  };
  int width;   
  int height;  
  int fps;
};
""".strip("\n")

        code_snippet = code_snippet_files[0].code_snippets[0]

        self.assertEqual(expect_content, code_snippet.source)

    def test_extract_enum(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
enum OPTIONAL_ENUM_SIZE_T {
  
  kMaxWidthInPixels = 3840,
  
  kMaxHeightInPixels = 2160,
  
  kMaxFps = 60,
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        expect_content = """
enum OPTIONAL_ENUM_SIZE_T {
  kMaxWidthInPixels = 3840,
  kMaxHeightInPixels = 2160,
  kMaxFps = 60,
};
""".strip("\n")

        code_snippet = code_snippet_files[0].code_snippets[0]

        self.assertEqual(expect_content, code_snippet.source)

    def test_extract_class(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
class AClass {
  
#if defined (_WIN32) || defined(__linux__) || defined(__ANDROID__)
  virtual int funcWithMacroSurround(const char* path, bool unload_after_use = false) = 0;
#endif

  virtual int funcWithoutParameterList() = 0;

  virtual int funcParameterList(const char* path, bool unload_after_use = false) = 0;
  
  virtual int funcMultiLineParameterList(const char* path,
                                       bool unload_after_use = false) = 0;
                                       
virtual int funcWithoutPrefixIndent() = 0;
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        code_snippet = code_snippet_files[0].code_snippets[0]

        self.assertTrue(isinstance(code_snippet, ChunkCodeSnippet))
        self.assertEqual(code_snippet.name, "AClass")

        code_snippets: List[CodeSnippet] = code_snippet.code_snippets

        self.assertEqual(len(code_snippets), 5)

        expect_content1 = """
#if defined (_WIN32) || defined(__linux__) || defined(__ANDROID__)
  virtual int funcWithMacroSurround(const char* path, bool unload_after_use = false) = 0;
#endif
""".strip("\n")
        self.assertEqual(code_snippets[0].source, expect_content1)

        expect_content2 = """
virtual int funcWithoutParameterList() = 0;
""".strip("\n")
        self.assertEqual(code_snippets[1].source, expect_content2)

        expect_content3 = """
virtual int funcParameterList(const char* path, bool unload_after_use = false) = 0;
""".strip("\n")
        self.assertEqual(code_snippets[2].source, expect_content3)

        expect_content4 = """
virtual int funcMultiLineParameterList(const char* path,
                                       bool unload_after_use = false) = 0;
""".strip("\n")
        self.assertEqual(code_snippets[3].source, expect_content4)

        expect_content5 = """
virtual int funcWithoutPrefixIndent() = 0;
""".strip("\n")
        self.assertEqual(code_snippets[4].source, expect_content5)

    def test_extract_relative_code_snippets(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
struct MyStruct {
  bool field1;
};

class AClass {
  virtual int funcParameterList(const MyStruct& my_struct) = 0;
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        code_snippet = code_snippet_files[0].code_snippets[1]

        self.assertTrue(isinstance(code_snippet, ChunkCodeSnippet))
        self.assertEqual(code_snippet.name, "AClass")

        code_snippets: List[CodeSnippet] = code_snippet.code_snippets

        self.assertEqual(len(code_snippets), 1)
        self.assertEqual(len(code_snippets[0].relative_code_snippets), 1)

        relative_code_snippet = code_snippets[0].relative_code_snippets[0]

        self.assertEqual(relative_code_snippet.name, "MyStruct")

        expect_content = """
struct MyStruct {
  bool field1;
};
""".strip("\n")
        self.assertEqual(relative_code_snippet.source, expect_content)

    def test_extract_relative_code_snippets_with_class(self):
        path = os.path.join(self.__tmp_dir.name, "cxx_file.h")
        with open(path, "w") as f:
            content = """
class MyEventHandler {
};

class AClass {
  virtual int registerEventHandler(const MyEventHandler* my_event) = 0;
};
"""
            f.write(content)

        code_snippet_files = self.__cxx_code_snippet_extractor.extract([path])

        code_snippet = code_snippet_files[0].code_snippets[1]

        self.assertTrue(isinstance(code_snippet, ChunkCodeSnippet))
        self.assertEqual(code_snippet.name, "AClass")

        code_snippets: List[CodeSnippet] = code_snippet.code_snippets

        self.assertEqual(len(code_snippets), 1)
        self.assertEqual(len(code_snippets[0].relative_code_snippets), 0)
