import asyncio
import os
import sys

# On Windows sandboxed environments where loopback socketpair hangs due to network isolation,
# mock the internal asyncio self-pipe so async routines run cleanly and reliably.
if sys.platform == "win32":
    try:
        import asyncio.proactor_events

        class DummySock:
            def setblocking(self, b): pass
            def fileno(self): return -1
            def close(self): pass
            def send(self, b): pass

        asyncio.proactor_events.BaseProactorEventLoop._make_self_pipe = (
            lambda self: setattr(self, "_ssock", DummySock())
            or setattr(self, "_csock", DummySock())
            or setattr(self, "_internal_fds", getattr(self, "_internal_fds", 0) + 1)
        )
        asyncio.proactor_events.BaseProactorEventLoop._loop_self_reading = lambda self, f=None: None
    except Exception:
        pass

# Ensure app is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tests.test_parser import (
    test_parse_empty_file_raises_corrupt_error,
    test_parse_nonexistent_file_raises_error,
    test_parse_minimal_valid_pdf_stream
)
from tests.test_chunker import (
    test_chunking_service_splits_and_preserves_page_numbers,
    test_chunking_service_ignores_empty_pages
)
from tests.test_embeddings import (
    test_mock_embedding_provider_properties,
    test_mock_embedding_provider_deterministic,
    test_embedding_service_batching
)
from tests.test_retrieval_and_isolation import (
    test_tenant_isolation_blocks_cross_user_retrieval
)
from tests.test_rag_generation import (
    test_rag_generation_with_evidence_produces_citations,
    test_rag_generation_insufficient_evidence,
    test_prompt_injection_resistance_in_document
)
from tests.test_tools_and_agent import (
    test_search_documents_tool,
    test_tool_invalid_arguments_raises_error,
    test_retrieve_document_page_tool,
    test_agent_service_loop
)
from tests.test_api_endpoints import (
    test_public_health_route,
    test_internal_health_route,
    test_verify_internal_key_security,
    test_chat_route,
    test_retrieval_route
)

def run_all_tests():
    tests = [
        ("PDF Parser - Empty file corrupt check", test_parse_empty_file_raises_corrupt_error),
        ("PDF Parser - Nonexistent file check", test_parse_nonexistent_file_raises_error),
        ("PDF Parser - Valid stream extraction", test_parse_minimal_valid_pdf_stream),
        ("Chunking - Splits & page boundaries", test_chunking_service_splits_and_preserves_page_numbers),
        ("Chunking - Ignores empty pages", test_chunking_service_ignores_empty_pages),
        ("Embeddings - Dimension & normalization", test_mock_embedding_provider_properties),
        ("Embeddings - Deterministic generation", test_mock_embedding_provider_deterministic),
        ("Embeddings - Batch calculation", test_embedding_service_batching),
        ("Security - Tenant isolation blocks cross-user retrieval", test_tenant_isolation_blocks_cross_user_retrieval),
        ("RAG - Answer generation with citations", test_rag_generation_with_evidence_produces_citations),
        ("RAG - Insufficient evidence handling", test_rag_generation_insufficient_evidence),
        ("Security - Prompt injection resistance", test_prompt_injection_resistance_in_document),
        ("Tools - search_documents tool", test_search_documents_tool),
        ("Tools - Argument validation error", test_tool_invalid_arguments_raises_error),
        ("Tools - retrieve_document_page tool", test_retrieve_document_page_tool),
        ("Agent - Multi-step agent reasoning loop", test_agent_service_loop),
        ("API - Public health route", test_public_health_route),
        ("API - Internal health route", test_internal_health_route),
        ("Security - Internal key authentication", test_verify_internal_key_security),
        ("API - Conversational chat route", test_chat_route),
        ("API - Semantic retrieval route", test_retrieval_route),
    ]

    passed = 0
    failed = 0
    print("=" * 60)
    print("KnowDoc Phase 4 AI Service Automated Test Suite")
    print("=" * 60)

    for name, test_fn in tests:
        try:
            test_fn()
            print(f"[PASS] {name}", flush=True)
            passed += 1
        except Exception as e:
            import traceback
            print(f"[FAIL] {name}:", flush=True)
            traceback.print_exc()
            failed += 1

    print("=" * 60, flush=True)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests", flush=True)
    print("=" * 60, flush=True)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
