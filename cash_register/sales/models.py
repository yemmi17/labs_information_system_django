from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class ProductGroup(models.Model):
    """Группа товаров для агрегации прибыли."""

    name = models.CharField("наименование группы", max_length=120, unique=True)

    class Meta:
        verbose_name = "группа товаров"
        verbose_name_plural = "группы товаров"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Sale(models.Model):
    """
    Строка продажи через кассу.
    Прибыль по заданию: (цена продажи без скидки × количество) − (цена закупки × количество).
    Поле скидки хранится в исходных данных; в формуле прибыли используется цена без скидки.
    """

    product_name = models.CharField("наименование товара", max_length=200)
    product_group = models.ForeignKey(
        ProductGroup,
        on_delete=models.PROTECT,
        related_name="sales",
        verbose_name="группа товара",
    )
    quantity = models.DecimalField(
        "проданное количество",
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
    )
    sale_price = models.DecimalField(
        "продажная цена (без скидки), за ед.",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Номинальная цена продажи за единицу до применения скидки.",
    )
    purchase_price = models.DecimalField(
        "закупочная цена, за ед.",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    discount = models.DecimalField(
        "скидка, %",
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Процент скидки с номинальной цены (для справки в исходных данных).",
    )

    class Meta:
        verbose_name = "продажа"
        verbose_name_plural = "продажи"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"{self.product_name} × {self.quantity}"

    @property
    def line_profit(self) -> Decimal:
        return (self.sale_price - self.purchase_price) * self.quantity
