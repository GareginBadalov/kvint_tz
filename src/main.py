import asyncio

from report_making_service import ReportMakingService

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    rms = ReportMakingService(loop)
    rms.loop.run_until_complete(rms.main())
