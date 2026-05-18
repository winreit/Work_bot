
class Paid_Works:
    def __init__(self):
        self.total_paid = 0


    def calculate_kp(self, total: int, number: str):
        """Расчёт КП по формуле - если сумма меньше 600р. по 52%, если больше - первые 600р тоже самое остальное 26%"""
        if total < 600:
            result = round(total * 0.52, 2)
        else:
            first_part = 600 * 0.52
            remainder = (total - 600) * 0.26
            result = round(first_part + remainder, 2)

        self.total_paid[number] = result
        print(result, '-', number)
        return result



