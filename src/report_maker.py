from collections import defaultdict
from datetime import datetime
from math import inf
from statistics import mean

import loguru


logger = loguru.logger


class ReportMaker:
    """
    Класс генератора отчетов
    """
    def __init__(self, data: list[dict], task: dict):
        """
        Конструктор класса генератора отчетов
        :param data: Данные для генерации отчета из data.json
        :param task: Задача полученная из rabbitMQ
        """
        self.task_received_time: datetime = datetime.now()
        self.data: list[dict] = [call_data for call_data in data if call_data["phone"] in task["phones"]]
        self.phones: list[int] = task["phones"]
        self.correlation_id: int = task["correlation_id"]

    async def calculate_data(self) -> list[dict]:
        """
        Основной метод расчета данных для отчета. Рассчитывает данные для номеров self.phones по данным из self.data
        :return: Список с данными по каждому номеру
        """
        result_data = defaultdict(lambda: {
            "phone": 0,
            "cnt_all_attempts": 0,
            "cnt_att_dur": {
                "10_sec": 0,
                "10_30_sec": 0,
                "30_sec": 0
            },
            "min_price_att": inf,
            "max_price_att": 0,
            "avg_dur_att": 0,
            "sum_price_att_over_15": 0
        })
        for call_data in self.data:
            phone_number = call_data["phone"]
            if phone_number in self.phones:
                result_data[phone_number]["phone"] = phone_number
                result_data[phone_number]["cnt_all_attempts"] += 1
                duration = (call_data["end_date"] - call_data["start_date"]) / 1000
                if "temp_durations" in result_data[phone_number]:
                    result_data[phone_number]["temp_durations"].append(duration)
                else:
                    result_data[phone_number]["temp_durations"] = [duration]
                price = duration * 10

                if duration <= 10:
                    result_data[phone_number]["cnt_att_dur"]["10_sec"] += 1
                elif duration <= 30:
                    result_data[phone_number]["cnt_att_dur"]["10_30_sec"] += 1
                else:
                    result_data[phone_number]["cnt_att_dur"]["30_sec"] += 1

                result_data[phone_number]["min_price_att"] = min(
                    result_data[phone_number]["min_price_att"], price
                ) if "min_price_att" in result_data[phone_number] else price

                result_data[phone_number]["max_price_att"] = max(
                    result_data[phone_number]["max_price_att"], price
                ) if "max_price_att" in result_data[phone_number] else price
        return [data for _, data in result_data.items()]

    @staticmethod
    async def data_post_processing(data: list[dict]) -> list[dict]:
        """
        Метод для расчета средней длительности звонка и удаления временной переменной из отчета
        :param data: Список с данными по каждому номеру
        :return: Тот же список, но с рассчитанным средним по продолжительности звонка
        """
        for data_by_phone in data:
            data_by_phone["avg_dur_att"] = mean(data_by_phone["temp_durations"])
            del data_by_phone["temp_durations"]
        return data

    async def make_report(self) -> dict:
        """
        Основной метод генератора отчетов
        :return: Готовый отчет
        """
        data = await self.calculate_data()
        result_data = await self.data_post_processing(data)
        result = {
            "correlation_id": self.correlation_id,
            "status": "Complete",
            "task_received": self.task_received_time.isoformat(),
            "from": "report_service",
            "to": "client",
            "data": result_data,
            "total_duration": str(datetime.now() - self.task_received_time)
        }
        logger.info(result)
        return result
