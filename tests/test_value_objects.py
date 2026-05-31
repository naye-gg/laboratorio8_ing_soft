"""Pruebas de los objetos de valor del dominio."""

from decimal import Decimal

import pytest

from restaurant_rewards.domain.value_objects import (
    CardNumber,
    DomainError,
    Money,
    RestaurantCode,
)


class TestMoney:
    def test_normaliza_a_dos_decimales(self):
        assert Money(Decimal("10.005")).amount == Decimal("10.01")

    def test_of_desde_float_evita_error_binario(self):
        assert Money.of(19.9).amount == Decimal("19.90")

    def test_of_desde_entero_y_string(self):
        assert Money.of(50).amount == Decimal("50.00")
        assert Money.of("3.5").amount == Decimal("3.50")

    def test_units_trunca_parte_entera(self):
        assert Money.of("99.99").units() == 99

    def test_multiplicacion(self):
        assert Money.of("100").multiplied_by(Decimal("0.05")).amount == Decimal("5.00")

    def test_str_formatea_dos_decimales(self):
        assert str(Money.of("7")) == "7.00"

    def test_rechaza_negativo(self):
        with pytest.raises(DomainError):
            Money(Decimal("-1"))

    def test_rechaza_valor_invalido(self):
        with pytest.raises(DomainError):
            Money.of("no-es-numero")


class TestCardNumber:
    def test_acepta_y_limpia_separadores(self):
        card = CardNumber("4111-1111 1111-1111")
        assert card.value == "4111111111111111"

    def test_enmascara_para_seguridad(self):
        assert CardNumber("4111111111111111").masked == "****1111"
        assert str(CardNumber("4111111111111111")) == "****1111"

    @pytest.mark.parametrize("valor", ["123", "12345678901234567890", "abcd"])
    def test_rechaza_longitud_o_formato_invalido(self, valor):
        with pytest.raises(DomainError):
            CardNumber(valor)


class TestRestaurantCode:
    def test_normaliza_a_mayusculas(self):
        assert RestaurantCode(" rest-001 ").value == "REST-001"

    def test_rechaza_vacio(self):
        with pytest.raises(DomainError):
            RestaurantCode("   ")

    def test_rechaza_demasiado_largo(self):
        with pytest.raises(DomainError):
            RestaurantCode("X" * 33)

    def test_str(self):
        assert str(RestaurantCode("rest-001")) == "REST-001"
