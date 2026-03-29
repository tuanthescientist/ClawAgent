# Changelog

## [3.0.0] - 2026-03-30
### Added
- Tích hợp Local LLM thật sự với Ollama (tự động phát hiện host, local mode)
- Hybrid LLM controller: OpenAI + Ollama + Groq + fallback chain, circuit breaker
- V3 integration trong `src/main.py` và `src/main_advanced.py`
- Cấu hình thử nghiệm `LLM_BACKEND=hybrid`, `OLLAMA_HOST`, `GROQ_API_KEY`
- `README.md` cập nhật với hướng dẫn v3.0, local LLM, và ví dụ hybrid
- `package.json` phiên bản 3.0.0 với metadata và keywords cập nhật
- GitHub release: tag `v3.0.0` đã publish

### Fixed
- Loại bỏ khởi tạo chỉ OpenAI trong `main.py` cũ
- Khắc phục thiếu phần hiển thị v3.0 ở Health endpoint
- Cấu trúc code mới dùng AppConfig và Kernel triage

### Docs
- Thêm `V3_INTEGRATION_COMPLETE.md` ghi nhận quá trình hoàn tất
- Thêm hướng dẫn v3.0 (UPGRADE_V3_IMPLEMENTATION_GUIDE.md, QUICKSTART_V3.md, v.v.)
