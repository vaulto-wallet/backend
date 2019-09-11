from typing import Dict

from cryptoassets.asset.asset import Asset, AssetErc20
from cryptoassets.asset.asset_type import AssetType
from cryptoassets.btc.btc_model import BitcoinClass
from cryptoassets.currency_model import CurrencyModel
from cryptoassets.eos.eos_model import EosModel
from cryptoassets.eth.erc20_model import Erc20Model
from cryptoassets.eth.eth_model import EthereumClass
from cryptoassets.explorers.btccom_explorer import BtcComExplorer
from cryptoassets.explorers.chain_so_explorer import ChainSoExplorer
from cryptoassets.tron.tron_model import TronModel
from cryptoassets.utils.singleton import Singleton
from cryptoassets.xrp.ripple_model import RippleModel


class CurrencyModelFactory(metaclass=Singleton):

    def __init__(self):
        self._models: Dict[str, CurrencyModel] = {}

    def _get_key(self, currency, network_type):
        return currency + "-" + network_type

    def get_currency_model_for_asset(self, asset: Asset, network_type: str) -> CurrencyModel:
        key = self._get_key(asset.symbol, network_type)
        if key in self._models:
            return self._models[key]

        if asset.asset_type == AssetType.ERC20:
            asset: AssetErc20 = asset
            key = self._get_key(asset.symbol, network_type)
            model = Erc20Model(network_type,
                               currency=asset.symbol,
                               decimals=asset.decimals,
                               coin_index=asset.coin_index,
                               contract_address=asset.contract_address)
            self._models[key] = model
            return model
        else:
            return self.get_currency_model(asset.symbol, network_type)

    def get_currency_model(self, currency: str, network_type: str) -> CurrencyModel:
        key = self._get_key(currency, network_type)
        if key in self._models:
            return self._models[key]
        if currency == "ETH":
            model = EthereumClass(network_type)
        elif currency == "BTC":
            model = BitcoinClass(network_type)
        elif currency == "BCH":
            model = BitcoinClass(network_type, symbol=currency,
                                 explorer=BtcComExplorer(currency, network_type))
        elif currency == "LTC":
            explorer = ChainSoExplorer.from_symbol_and_network_type(currency, network_type)
            model = BitcoinClass(network_type, symbol=currency, explorer=explorer)
        elif currency == "XRP":
            model = RippleModel(network_type)
        elif currency == "EOS":
            model = EosModel(network_type)
        elif currency == "TRX":
            model = TronModel(network_type)
        else:
            raise NotImplementedError(f"Unsupported currency: {currency}")
        self._models[key] = model
        return model
