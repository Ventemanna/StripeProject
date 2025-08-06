from django.db import models

class Items(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}. За {self.price}"

class Orders(models.Model):
    item = models.ManyToManyField(Items, through="ItemOrder")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

class ItemOrder(models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)