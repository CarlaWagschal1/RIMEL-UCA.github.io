#!/usr/bin/env python
# coding: utf-8

# Examples require an initialized GsSession and relevant entitlements. `run_analytics` scope is required for the functionality covered in this tutorial. External clients need to substitute thier own client id and client secret below. Please refer to <a href="https://developer.gs.com/docs/gsquant/guides/Authentication/2-gs-session/"> Sessions</a> for details.

# In[ ]:


from gs_quant.session import GsSession
GsSession.use(client_id=None, client_secret=None, scopes=('run_analytics',))

# ## What is a Portfolio
# 
# Portfolios are collections of instruments. They can be used to simplify calculations and syntax when working with many instruments. [All `Priceable` methods](https://developer.gs.com/docs/gsquant/api/classes/gs_quant.base.Priceable.html#gs_quant.base.Priceable/#methods/) like `price`, `as_dict`, and `calc` are also available for a `Portfolio`. When evaluated on a portfolio, a user can still access results for individual instruments in that portfolio.

# ## How to Create a Portfolio

# Let's first create a few instruments that will be included in our portfolio. To learn more about instruments and how to create them please see the [instruments guide](https://developer.gs.com/docs/gsquant/guides/Pricing-and-Risk/instruments/) and [tutorial](https://developer.gs.com/docs/gsquant/tutorials/Pricing-and-Risk/1-creating-an-instrument/). 

# In[ ]:


from gs_quant.instrument import IRSwaption
from gs_quant.common import PayReceive, Currency
swaption1 = IRSwaption(PayReceive.Pay, '5y', Currency.EUR, expiration_date='3m', name='EUR-5y3m')
swaption2 = IRSwaption(PayReceive.Pay, '5y', Currency.EUR, expiration_date='6m', name='EUR-5y6m')

# We can now import `Portfolio` and add the two swaptions we created.

# In[ ]:


from gs_quant.markets.portfolio import Portfolio
portfolio = Portfolio((swaption1, swaption2))

# Portfolio constituents can also be set (or reset) by assiging to instruments.

# In[ ]:


portfolio.pricables = (swaption1, swaption2)

# ## How to Refer to Specific Instruments in a Portfolio
# 
# Instruments can be referred to by position, by instrument object and by name. Examples of each below.

# In[ ]:


portfolio[0] # by position
portfolio[swaption2] # by instrument object
portfolio['EUR-5y6m'] # by instrument name

# ## How to Work with Portfolios
# 
# As mentioned above, working with portfolios is same as working with instruments and the same methods are available including `resolve`, `price`, `calc`. Any calculations on a portfolio can be aggregated on a portfolio level using `aggregate.` Let's look at each below.

# In[ ]:


portfolio.resolve() # resolve
portfolio.price().aggregate() # price

# In[ ]:


# calculate risk measures
import gs_quant.risk as risk
result = portfolio.calc((risk.DollarPrice, risk.IRDelta))

# Instrument-level results can be accessed through either indexing into the measure or the instrument first. See [above](#How-to-Refer-to-Specific-Instruments-in-a-Portfolio) on ways the instruments can be referred to.

# In[ ]:


result[risk.DollarPrice]['EUR-5y3m'] # or
result['EUR-5y3m'][risk.DollarPrice]

# Portfolio-level results can be aggregated using `aggregate`.

# In[ ]:


price = result[risk.DollarPrice].aggregate()
delta = result[risk.IRDelta].aggregate()

# #### Disclaimer
# This website may contain links to websites and the content of third parties ("Third Party Content"). We do not monitor, review or update, and do not have any control over, any Third Party Content or third party websites. We make no representation, warranty or guarantee as to the accuracy, completeness, timeliness or reliability of any Third Party Content and are not responsible for any loss or damage of any sort resulting from the use of, or for any failure of, products or services provided at or from a third party resource. If you use these links and the Third Party Content, you acknowledge that you are doing so entirely at your own risk.
