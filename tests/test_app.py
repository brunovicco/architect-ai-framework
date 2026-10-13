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
