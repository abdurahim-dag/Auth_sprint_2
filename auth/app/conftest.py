"""Модуль фикстур"""
import app.config


pytest_plugins = [
    "app.tests.functional.fixtures.api",
    "app.tests.functional.fixtures.db",
]

app.config.settings = app.config.Settings()
