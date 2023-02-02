#!/usr/bin/env python
# coding: utf-8

# Examples require an initialized GsSession and relevant entitlements. External clients need to substitute thier own client id and client secret below. Please refer to <a href="https://developer.gs.com/docs/gsquant/guides/Authentication/2-gs-session/"> Sessions</a> for details.

# In[ ]:


from gs_quant.session import GsSession
GsSession.use(client_id=None, client_secret=None, scopes=('run_analytics',))

# ## What is Pricing Context
# 
# [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) is a class used for controlling pricing, market data and computation behavior when pricing instruments and calculating risk.
# It can be used to provide a common context which can be reused for a number of different data access or manipulation functions.
# 
# More specifically, [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) can be used to define pricing date, date for sourcing market data, market data location as well as whether the calculation should be processed
# asynchronously or batched.
# 
# [`HistoricalPricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.HistoricalPricingContext.html) is also available to produce valuations over multiple dates. Both [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) and [`HistoricalPricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.HistoricalPricingContext.html) are distinct from the `MarketDataContext` which provides a market state as of a given date.
# 

# ## Evaluating Pricing and Risk Using A Context
# 
# Pricing date is used to compute the expiration date and discounting rules for a derivative instrument. For example, the expiration date of a 1-month forward will be 1 month from the current pricing date.
# `pricing_date` is different from `market_data_as_of` which is the date for sourcing market data and is defaulted to 1 business day before `pricing_date`.
# 
# <note> For information on how to define an instrument and compute price and risk for it, please refer to <a href="https://developer.gs.com/docs/gsquant/guides/Pricing-and-Risk/instruments/">Instruments</a> and <a href="https://developer.gs.com/docs/gsquant/guides/Pricing-and-Risk/measures/">Measures</a>, respectively, for details. </note>
# 
# Let's import [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) and examine the current pricing date. It is defaulted to today when pricing an instrument.
# 

# In[ ]:


from gs_quant.markets import PricingContext

PricingContext.current.pricing_date

# If you wish to change the default behaviour, you can change the default pricing context:

# In[ ]:


import datetime as dt
from gs_quant.datetime import business_day_offset

PricingContext.current = PricingContext(
    pricing_date=business_day_offset(dt.date.today(), -1, roll='preceding'),
    market_data_location='NYC')

# We define an [`IRSwaption`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.instrument.IRSwaption.html#gs_quant.instrument.IRSwaption/) below:

# In[ ]:


from gs_quant.instrument import IRSwaption
from gs_quant.common import Currency, PayReceive
swaption = IRSwaption(PayReceive.Receive, '5y', Currency.USD, expiration_date='13m', strike='atm+40', notional_amount=1e8)

# A [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) may also be used as a context manager, to temporarily change pricing parameters for the scope of a computation:

# In[ ]:


custom_date = dt.date(2019, 5, 31)

with PricingContext(pricing_date=custom_date):
    swaption.resolve()
    price_f = swaption.price()

print(swaption.as_dict())
print(price_f.result())

# Note that using a [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) as a context manager has two extra effects:
# 
# 1. All calls to [`price()`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.base.Priceable.html#gs_quant.base.Priceable.price), [`calc()`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.base.Priceable.html#gs_quant.base.Priceable.calc) are dispatched as a single request, on context manager exit. This allows for the communication overhead to be borne only once for multiple calculations.
# 2. The results of these calls will be futures, whose result is the original data type. Thus, `calc(risk.IRDelta)` will return a future whose result will be a pandas DataFrame and
# [`dollar_price()`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.base.Priceable.html#gs_quant.base.Priceable.dollar_price), will return a future whose result will be a float.
# 
# PricingContext has optional parameters of `is_async` and `is_batch`, which are discussed [below](#Controlling-Computation-Behavior).

# ## Historical Pricing Context
# 
# [`HistoricalPricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.HistoricalPricingContext.html) can be used to evaluate instruments for a range of parameters, like the date range below.

# In[ ]:


from gs_quant.markets import HistoricalPricingContext
import gs_quant.risk as risk

start_date = dt.date(2019, 5, 1)
end_date = dt.date(2019, 5, 31)

with HistoricalPricingContext(start_date, end_date):
    swaption_vega_f = swaption.calc(risk.IRVega)

swaption_vega = swaption_vega_f.result()
swaption_vega.head()

# 
# ## Controlling Computation Behavior
# 
# There are two parameters of [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) which determine how the calculation call should be made: `is_async` and `is_batch`. There are several considerations when deciding what the preferred behavior is.
# 
# ### Async
# 
# `is_async` determines whether the request is processed asynchronously. This allows a unit of work to run separately from the primary application thread.
# 
# If `False` (the default) the `__exit__` method of [`PricingContext`](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.markets.PricingContext.html) will block until the results are returned. If `True`, it will return immediately and the user should check the status of the returned futures, or add a callback to them in order to handle results.
# 
# Setting `is_async=True` allows other work to be done while waiting for calculation results. It is best used for processing independent data; asynchronously updating records that are dependent or depended upon may lead to unexpected results.
# 
# ### Batch
# 
# Calculation requests are handled by HTTP calls. The gateway which processes these calls has a maximum timeout of 3 minutes.
# For calculations that are expected to last longer than 3 minutes, `is_batch` should be set to `True`.
# In this mode, the computation is run asynchronously on Goldman Sachs' servers and a thread is started to listen for the results.
# 
# `is_batch` is independent of `is_async` and may be used with `is_async` set either to `True` or `False`.
# 
# Currently `is_batch=True` adds a small overhead to calculations. This will be eliminated in the future, at which point we will likely to make all calculations execute this way, and eliminate the `is_batch` option.
# 
# 
# ### Pricing Context with Async and Batch
# 
# In the example below we will examine the behavior of async and batch. We will price and calculate vega for an Interest Rate Swaption over May 2019 and do
# some 'work' while waiting for the result. Based on the output, one can see that some useful work can be done by setting `is_async=True` but changing `is_batch=True` doesn't
# offer any additional speed-up.

# In[ ]:


from time import sleep

# create swaption
swaption = IRSwaption(PayReceive.Receive, '5y', Currency.USD, expiration_date='13m', strike='atm+40', notional_amount=1e8)

start_date = dt.date(2019, 5, 1)
end_date = dt.date(2019, 5, 31)

# price over date range with both async and batch = True
with HistoricalPricingContext(start_date, end_date, is_async=True, is_batch=True):
    swaption_price = swaption.price()
    swaption_vega  = swaption.calc(risk.IRVega)

# Do some work while waiting for results. All futures will be completed on exit of PricingContext
n = 0
while not swaption_price.done():
    print(n)
    n += 1
    sleep(1)

swaption_prices = swaption_price.result()
swaption_vegas  = swaption_vega.result()

# #### Disclaimer
# This website may contain links to websites and the content of third parties ("Third Party Content"). We do not monitor, review or update, and do not have any control over, any Third Party Content or third party websites. We make no representation, warranty or guarantee as to the accuracy, completeness, timeliness or reliability of any Third Party Content and are not responsible for any loss or damage of any sort resulting from the use of, or for any failure of, products or services provided at or from a third party resource. If you use these links and the Third Party Content, you acknowledge that you are doing so entirely at your own risk.
