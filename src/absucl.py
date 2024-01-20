from GS.proof import GS
from GS.elements import ZpElement, G1Element, G2Element, GTElement
from GS.equations import Equation, QEquation, MS1Equation, MS2Equation, PPEquation, Variable, Constant, AMapRight, AMapLeft, AMapBoth
from ds import FBB as DS
from lit import WBB as LIT
from rpsps import RPSPS
from msp import MSP

from typing import Dict, List, Tuple
import json


class ABSUCL():
    def __init__(self, gs: GS, psps: RPSPS, ds: DS, lit: LIT, sk_psdo: List[ZpElement], vk_psdo: List[G2Element]):
        self.gs = gs
        self.psps = psps
        self.ds = ds
        self.lit = lit
        self.sk_psdo = sk_psdo
        self.vk_psdo = vk_psdo
        self.vk_attrs: Dict[str, G2Element] = {}

    @classmethod
    def setup(cls):
        gs = GS.setup()
        psps = RPSPS(gs.CRS)
        ds = DS(gs.CRS)
        lit = LIT(gs.CRS)
        sk_psdo,vk_psdo = ds.keygen()
        return cls(gs, psps, ds, lit, sk_psdo, vk_psdo)

    @classmethod
    def setup_from_json(cls, json_str:str):
        gs = GS.from_json(json_str)
        json_dict = json.loads(json_str)
        sk_psdo = [ZpElement.from_json(zp) for zp in json_dict['sk_psdo']] if 'sk_psdo' in json_dict else [None]
        vk_psdo = [G2Element.from_json(g2) for g2 in json_dict['vk_psdo']]

        psps = RPSPS(gs.CRS)
        ds = DS(gs.CRS)
        lit = LIT(gs.CRS)
        key = ds.keygen()
        return cls(gs, psps, ds, lit, sk_psdo, vk_psdo)

    def add_vk_attr(self, attribute:str, vk_aa:G2Element):
        self.vk_attrs[attribute] = vk_aa

    def aa_setup(self) -> Tuple[List[ZpElement], List[G2Element]]:
        sk,vk = self.psps.keygen()
        return sk, vk

    def user_keygen(self) -> Tuple[ZpElement, G2Element]:
        sk,vk = self.lit.keygen()
        return sk, vk

    def attr_keygen(self, fusk:G1Element, attribute:str, sk_aa:ZpElement) -> Tuple[G1Element, G1Element]:
        element_attr = ZpElement.from_str(attribute)
        #sk_ida = self.psps.sign(sk_aa, ((fusk, None), [attribute]))
        sk_ida = self.psps.sign(sk_aa, ((fusk, None), [element_attr]))
        return sk_ida

    def sign(self, m:str, predicate:str, usk:ZpElement, sk_ida_dict:Dict[str, Tuple[G1Element, G1Element]], recip:int):
        psdo_attr = ZpElement.hash_from_string(f"{m}{predicate}{recip}")
        #xpredicate = f"({predicate}) or {psdo_attr}"
        xpredicate = f"({predicate}) or PSDO"
        msp = MSP.from_policy_str(xpredicate)

        for attr_name in msp.index:
            if not attr_name in self.vk_attrs:
                if attr_name == "PSDO": continue
                raise Exception(f"Attribute {attr_name} not found in attribute authorities")

        randomized_sk_ida = {}

        for attr_name in msp.index:
            if attr_name in sk_ida_dict:
                randomized_sk_ida[attr_name] = RPSPS.randomize(sk_ida_dict[attr_name])
            else:
                if attr_name == "PSDO":
                    randomized_sk_ida[attr_name] = (G1Element.random(), ZpElement.random())
                    continue
                randomized_sk_ida[attr_name] = (G1Element.random(), G1Element.random())

        # TODO: Change method name to tag instead of sign
        tag = self.lit.sign(usk, ZpElement.init(recip))


        # Witnesses
        witnesses = {}
        for attr_name in msp.index:
            witnesses[f"z_{attr_name}"] = ZpElement.init(0) if attr_name not in sk_ida_dict else ZpElement.init(1)
            z_attr = f"z_{attr_name}"
            #witnesses[f"R_{attr_name}"] = randomized_sk_ida[attr_name][0] NOT A WITNESS!!!!
            if attr_name == "PSDO": continue
            witnesses[f"Rsmile_{attr_name}"] = witnesses[f"z_{attr_name}"] * randomized_sk_ida[attr_name][0]
            witnesses[f"S_{attr_name}"] = randomized_sk_ida[attr_name][1]
            witnesses[f"Ssmile_{attr_name}"] = witnesses[f"z_{attr_name}"] * witnesses[f"S_{attr_name}"]
        witnesses["F"] = usk * self.g
        witnesses["Ftilda"] = usk * self.h
        witnesses["sigma"] = randomized_sk_ida["PSDO"][0]
        witnesses["sigmasmile"] = witnesses["z_PSDO"] * randomized_sk_ida["PSDO"][0]
        witnesses["Gsmile"] = witnesses["z_PSDO"] * self.g

        variables = {k: Variable(k, v) for k,v in witnesses.items()}

        # Equations
        # 1. MSP equations
        msp_eqs = []

        # First column
        first_column_amaps = []
        for i,attr_name in enumerate(msp.index):
            Mz = AMapRight(Constant(msp.msp[i][0]), variables[f"z_{attr_name}"])
            first_column_amaps.append(Mz)
        msp_eq0 = QEquation("msp_0", first_column_amaps, Constant(ZpElement.init(1)))
        msp_eq0._validate()
        msp_eqs.append(msp_eq0)

        # Other columns
        for column in range(1, msp.width):
            column_amaps = []
            for i,attr_name in enumerate(msp.index):
                Mz = AMapRight(Constant(msp.msp[i][column]), variables[f"z_{attr_name}"])
                column_amaps.append(Mz)
            msp_eq = QEquation(f"msp_{column}", column_amaps, Constant(ZpElement.init(0)))
            msp_eq._validate()
            msp_eqs.append(msp_eq)

        # 2. Tag equation
        tag_amap = AMapRight(Constant(tag), variables["Ftilda"])
        tag_target = Constant(self.g.pair(self.h) * ~tag.pair(ZpElement.init(recip) * self.h))
        tag_eq = PPEquation("tag", [tag_amap], tag_target)
        tag_eq._validate()

        # 3. Is Consistent equation
        is_consistent_amap1 = AMapLeft(variables["F"], Constant(self.h))
        is_consistent_amap2 = AMapRight(Constant(~self.g), variables["Ftilda"])
        is_consistent_target = Constant(GTElement.zero())
        is_consistent_eq = PPEquation("is_consistent", [is_consistent_amap1, is_consistent_amap2], is_consistent_target)
        is_consistent_eq._validate()

        # 4. RPSPS verify equations
        rpsps_eqs = []
        for attr_name in msp.index:
            if attr_name == "PSDO":
                continue
            S_amap1 = AMapBoth(variables[f"S_{attr_name}"], variables[f"z_{attr_name}"])
            S_amap2 = AMapLeft(variables[f"Ssmile_{attr_name}"], Constant(ZpElement.init(-1)))
            S_eq = MS1Equation(f"S_{attr_name}", [S_amap1, S_amap2], Constant(G1Element.zero()))
            S_eq._validate()

            R_amap1 = AMapRight(Constant(randomized_sk_ida[attr_name][0]), variables[f"z_{attr_name}"])
            R_amap2 = AMapLeft(variables[f"Rsmile_{attr_name}"], Constant(ZpElement.init(-1)))
            R_eq = MS1Equation(f"R_{attr_name}", [R_amap1, R_amap2], Constant(G1Element.zero()))
            R_eq._validate()

            a_attr = ZpElement.from_str(attr_name)
            V_amap1 = AMapBoth(variables[f"Rsmile_{attr_name}"], variables["Ftilda"])
            V_amap2 = AMapLeft(variables[f"Rsmile_{attr_name}"], Constant(self.vk_attrs[attr_name][0])) # vk_attrs[name] => [X,Y,Z]
            V_amap3 = AMapLeft(variables[f"Rsmile_{attr_name}"], Constant(a_attr * self.vk_attrs[attr_name][1]))
            V_amap4 = AMapLeft(variables[f"Ssmile_{attr_name}"], Constant(~self.vk_attrs[attr_name][2]))
            V_eq = PPEquation(f"V_{attr_name}", [V_amap1, V_amap2, V_amap3, V_amap4], Constant(GTElement.zero()))
            V_eq._validate()

            rpsps_eqs.append(S_eq)
            rpsps_eqs.append(R_eq)
            rpsps_eqs.append(V_eq)

        # 5. psdo verify equations
        sigma_amap1 = AMapBoth(variables["sigma"], variables["z_PSDO"])
        sigma_amap2 = AMapLeft(variables["sigmasmile"], Constant(ZpElement.init(-1)))
        sigma_eq = MS1Equation("sigma", [sigma_amap1, sigma_amap2], Constant(G1Element.zero()))
        sigma_eq._validate()

        G_amap1 = AMapRight(Constant(self.g), variables["z_PSDO"])
        G_amap2 = AMapLeft(variables["Gsmile"], Constant(ZpElement.init(-1)))
        G_eq = MS1Equation("G", [G_amap1, G_amap2], Constant(G1Element.zero()))
        G_eq._validate()

        #fbb_amap1 = AMapLeft(variables['sigmasmile'], Constant(self.vk_psdo[0] + self.vk_psdo[1] + psdo_attr * self.h)) # TODO: This wont work!!!
        fbb_amap1 = AMapLeft(variables['sigmasmile'], Constant(self.vk_psdo[0] + self.vk_psdo[1] + ZpElement.random() * self.h)) # TODO: Could be anything?
        fbb_amap2 = AMapLeft(variables['Gsmile'], Constant(self.h))
        fbb_eq = PPEquation("fbb", [fbb_amap1, fbb_amap2], Constant(GTElement.zero()))
        fbb_eq._validate()

        psdo_eqs = [sigma_eq, G_eq, fbb_eq]


        eqs = msp_eqs + [tag_eq, is_consistent_eq] + rpsps_eqs + psdo_eqs
        proof = self.gs.prove(eqs, variables)

        # TODO: delete eqs... Just to prove that it works
        return proof, eqs



    def verify(self):
        pass

    def link(self):
        pass

    def identify(self):
        pass

    @property
    def CRS(self):
        return self.gs.CRS

    @property
    def g(self):
        return self.gs.g

    @property
    def h(self):
        return self.gs.h

    @property
    def xk(self):
        return self.gs.trapdoor

    @property
    def svk(self):
        return self.key.svk

    @property
    def ssk(self):
        return self.key.ssk


class Attribute:
    def __init__(self, name:str, authority:str, value:str):
        self.name = name
        self.authority = authority
        self.value = value

    @classmethod
    def from_str(cls, string:str, authority:str):
        name = string
        authority = authority
        full_name = f"{name}@{authority}"
        value = ZpElement.from_str(full_name)
        return cls(name, authority, value)


    def __str__(self):
        return self.name


class AttributeAuthority:
    def __init__(self, name:str, absucl:ABSUCL, vk:List[G2Element], sk:List[ZpElement]):
        self.name = name
        self.absucl = absucl
        self.vk = vk
        self.sk = sk

    @classmethod
    def new_authority(cls, name:str, absucl:ABSUCL):
        sk, vk = absucl.aa_setup()
        return cls(name, absucl, vk, sk)

    def sign_attribute(self, name:str, fusk:G1Element):
        attribute = Attribute.from_str(name, self.name)
        #sk_ida = self.absucl.attr_keygen(fusk, attribute.value, self.sk)
        sk_ida = self.absucl.attr_keygen(fusk, f"{attribute.name}@{self.name}", self.sk)
        return attribute, sk_ida


class User:
    def __init__(self, name:str, absucl:ABSUCL, vk:G2Element, sk:ZpElement):
        self.name = name
        self.absucl = absucl
        self.vk = vk
        self.sk = sk
        self.attributes: Dict[str, Tuple[G1Element, G1Element]] = {}
    
    @property
    def f(self):
        return self.sk * self.absucl.g

    @classmethod
    def new_user(cls, name:str, absucl:ABSUCL):
        sk, vk = absucl.user_keygen()
        return cls(name, absucl, vk, sk)

    def add_attribute(self, attribute:Attribute, sk_ida: Tuple[G1Element, G1Element]):
        self.attributes[attribute.name] = sk_ida





