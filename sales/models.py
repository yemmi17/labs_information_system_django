from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Client(models.Model):
    name = models.CharField("Имя клиента", max_length=255, unique=True)
    comment = models.TextField("Комментарий", blank=True)

    total_purchases = models.DecimalField(
        "Общий счёт покупок",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    current_balance = models.DecimalField(
        "Текущий счёт клиента (предоплата)",
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    credit_limit = models.DecimalField(
        "Потолок кредита",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    current_debt = models.DecimalField(
        "Текущий долг",
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name

    @property
    def credit_remaining(self):
        return self.credit_limit - self.current_debt

    @property
    def credit_usage_ratio(self):
        if self.credit_limit <= 0:
            return 0
        return float(self.current_debt / self.credit_limit)


class Product(models.Model):
    name = models.CharField("Наименование", max_length=255, unique=True)
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.DecimalField(
        "Остаток на складе",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class Order(models.Model):
    class SaleType(models.TextChoices):
        CASH = "cash", "Наличный расчет"
        NONCASH = "noncash", "Безналичный расчет"
        CREDIT = "credit", "Кредит"
        BARTER = "barter", "Бартер"
        OFFSET = "offset", "Взаимозачёт"

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders")
    created_at = models.DateTimeField(default=timezone.now)
    sale_type = models.CharField(
        "Вид продажи",
        max_length=20,
        choices=SaleType.choices,
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} ({self.client})"

    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.DecimalField(
        "Количество",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    @property
    def line_total(self):
        return self.quantity * self.price
