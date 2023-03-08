from scipy.stats import skewnorm, norm, randint
import numpy as np


class MarketDataProvider:
    def __init__(self, dt, T):
        self.dt = dt
        self.T = T
        
    def receive_orders(self):
        raise NotImplementedError

        
class BrownianMotionDataProvider(MarketDataProvider):
    def __init__(self, dt, T, mu, sigma, s0, tick = 0.05, skewness=5):
        self.dt = dt
        self.T = T
        self.mu = mu
        self.sigma = sigma
        self.s0 = s0
        self.skewness = skewness
        self.wiener = 0
        self.time = 0
        self.tick = tick

    def receive_orders(self):
        self.wiener += norm.rvs(loc=0, scale=self.dt)
        fair_price = self.s0 * np.exp((self.mu - self.sigma**2 / 2) * self.time + self.sigma * self.wiener)
        self.time += self.dt
        
        bids, asks, histb, hista = self.get_bid_ask()
        bids = 0.5*(bids[1:] + bids[:-1])
        asks = 0.5*(asks[1:] + asks[:-1])
        bids = np.round(bids + fair_price, 2)
        asks = np.round(asks + fair_price, 2)
        
        is_bid, is_ask = np.ones_like(bids), np.zeros_like(asks)
        prices = np.append(bids, asks)
        shares = np.append(histb, hista)
        classes = np.append(is_bid, is_ask)
        
        assert len(classes) == len(prices)
        indecies = np.random.permutation(len(prices))
        
        return prices[indecies], shares[indecies], classes[indecies]
    
    
    def get_bid_ask(self):
        bid_num = randint.rvs(10, 100)
        ask_num = randint.rvs(10, 100)
        
        bids = skewnorm.rvs(a=self.skewness, scale=self.tick, size=bid_num)
        asks = skewnorm.rvs(a=-self.skewness, scale=self.tick, size=ask_num)
        shift = np.mean(bids) - np.mean(asks)
        
        bids -= 1.5 * shift
        asks += 1.5 * shift

        histb, bids = np.histogram(bids, bins=bid_num)
        hista, asks = np.histogram(asks, bins=ask_num)
        
        return bids, asks, histb, hista