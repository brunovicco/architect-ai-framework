"""Regression coverage for decisions restored across Streamlit reruns."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_example_preserves_selected_option_and_deterministic_gate():
    app = AppTest.from_file(str(Path(__file__).parents[1] / 'app.py')).run()
    assert not app.exception
    next(button for button in app.button if 'Investment Assistant' in button.label).click().run()
    assert not app.exception
    assert app.selectbox(key='selected_option').value == 'Agente + ferramentas de API'
    app.checkbox(key='dynamic_tool_choice').uncheck().run()
    app.checkbox(key='deterministic_sufficient').check().run()
    assert not app.exception
    assert any(metric.value == 'Software determinístico' for metric in app.metric)
    app.selectbox(key='lang').select('en').run()
    assert not app.exception
    assert app.checkbox(key='deterministic_sufficient').value
    assert any(metric.value == 'Deterministic software' for metric in app.metric)
    assert app.selectbox(key='selected_option').value == 'Agente + ferramentas de API'


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
    next(button for button in app.button if 'Investment Assistant' in button.label).click().run()
    assert app.slider(key=key).value == 4
    app.slider(key=key).set_value(2).run()
    app.selectbox(key='lang').select('en').run()
    assert app.slider(key=key).value == 2
    next(button for button in app.button if button.label == "Clear form").click().run()
    assert app.slider(key=key).value == 3
    assert not app.exception
    assert 'created with a default value' not in caplog.text
