"""Regression coverage for decisions restored across Streamlit reruns."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def test_example_preserves_selected_option_and_deterministic_gate():
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    assert not app.exception
    assert app.selectbox(key='example_choice').value == 'investment_assistant'
    next(button for button in app.button if button.label == 'Carregar exemplo').click().run()
    assert not app.exception
    assert app.selectbox(key='selected_option').value == 'Workflow + Roteamento'
    app.checkbox(key='dynamic_tool_choice').uncheck().run()
    app.checkbox(key='deterministic_sufficient').check().run()
    assert not app.exception
    assert any(metric.value == 'Software determinístico' for metric in app.metric)
    app.selectbox(key='lang').select('en').run()
    assert not app.exception
    assert app.checkbox(key='deterministic_sufficient').value
    assert any(metric.value == 'Deterministic software' for metric in app.metric)
    assert app.selectbox(key='selected_option').value == 'Workflow + Roteamento'


@pytest.mark.parametrize(("example_key", "expected_architecture"), [
    ("investment_assistant", "Workflow"),
    ("deterministic_order_lookup", "Software determinístico"),
    ("policy_qa_assistant", "LLM Aumentado"),
    ("research_agent", "Agente"),
    ("support_orchestrator", "Multiagente"),
])
def test_each_bundled_example_loads_without_exception(example_key, expected_architecture):
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    app.selectbox(key='example_choice').select(example_key).run()
    next(button for button in app.button if button.label == 'Carregar exemplo').click().run()
    assert not app.exception
    assert any(metric.value == expected_architecture for metric in app.metric)


def test_changing_plan_discards_old_ai_review():
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    app.session_state['ai_review_result'] = 'Old review'
    app.text_input(key='name').set_value('A changed case').run()
    assert not app.exception
    assert 'ai_review_result' not in app.session_state


def test_tradeoff_scores_restore_edit_and_reset_without_duplicate_defaults(monkeypatch, caplog):
    from streamlit.elements.lib import policies

    monkeypatch.setattr(policies, "_shown_default_value_warning", False)
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    key = '0-Quality/task success'
    assert app.slider(key=key).value == 3
    next(button for button in app.button if button.label == 'Carregar exemplo').click().run()
    assert app.slider(key=key).value == 4
    app.slider(key=key).set_value(2).run()
    app.selectbox(key='lang').select('en').run()
    assert app.slider(key=key).value == 2
    next(button for button in app.button if button.label == "Clear form").click().run()
    assert app.slider(key=key).value == 3
    assert not app.exception
    assert 'created with a default value' not in caplog.text


def test_unnamed_options_never_enter_selection_or_export(monkeypatch):
    import architect.exporters as exporters

    captured = []
    original = exporters.to_markdown

    def capture(plan, lang='en'):
        captured.append(plan)
        return original(plan, lang)

    monkeypatch.setattr(exporters, 'to_markdown', capture)
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    app.selectbox(key='example_choice').select('deterministic_order_lookup').run()
    next(b for b in app.button if b.label == 'Carregar exemplo').click().run()
    assert len(app.selectbox(key='selected_option').options) == 2
    assert len(captured[-1].option_scores) == 2
    assert all(option.name.strip() for option in captured[-1].option_scores)
    for key in ('option_a_name', 'option_b_name', 'option_c_name'):
        app.text_input(key=key).set_value(' ').run()
    assert not app.exception
    assert captured[-1].option_scores == []
    assert captured[-1].selected_option == ''
    app.text_input(key='option_b_name').set_value('New option').run()
    assert not app.exception
    assert app.selectbox(key='selected_option').value == 'New option'
    assert len(captured[-1].option_scores) == 1


def test_sensitivity_shows_conflicting_assumptions_in_ui():
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    next(b for b in app.button if b.label == 'Carregar exemplo').click().run()
    assert not app.exception
    assert any('conflita com sinais de autonomia' in warning.value for warning in app.warning)
