from framework import CRS, Equation, equations, verify
from utils import NamedArray, UnamedArray
import numpy as np
import elements as elements

crs = CRS.from_json({'u1': ['eJxNTTsOwjAMvYqVOUMcYjvlKghFBXXrFkBCiLvznGZgsPX8fv6E1u772ntr4Uzh9n5sPUQC+1r35zbYS1kiSY1kp0icCoA4wKpgKvuBVTMAQ1aZPgfiB6OBc3LaIi0A5gE7Os0FxgOdwwxF7D+cRgM+FARUMTb9MgUdtjyXW6wettGgcv3+AHQkMFg=', 'eJw9jc0OAiEMhF+l4cyBstAWX8UYspq97W3VxBjf3eFHDw2db6bD29V629fjqNWdyF1f9+1wnkCf6/7YOj2n4imbJ108cYAQCMGrCYYCMnsyuBo9lQ4EDsZkQG1X2NMyAp21YAyzBmMYRVNBvfEIZwSlBQMWK6O1HTDH+fFfJfvh2FrC9CVfPl9pfC9D'], 'u2': ['eJxFjsEKwyAQRH9FPHtwjbraXylB0pBbbqaFUvrvHXeFHmZlnrOOH9vafm69t2Zvxj7e19GtM6Cv7XweQu+xOpOKMxliiILH8ARK05WAqwVnBoTKMhOVYSBOUBwQ6RQUEJEaoqyxERdDXgbaRru0+rnF/H+WPG7j+FvV0ow1RgVXZaK0fn+M3C+R', 'eJw9jsEOAiEMRH+l4cyBYoHir5gNWc3e9oaaGOO/O4XVA6XzmE55u9Zu+9p7a+5M7vq6b915An2u+2Mb9CLVU1JPJXpizrNRMQHKIXjK1nA8isZJEl44omiBYNwJh80VDoFoPVkI4gSukkxgVkDVMmQ6xthw1fmB8gOp/HcDyfjJSBm5dS7Jefl8AUCGMBQ='], 'v1': ['eJxNUEEOAiEM/ArhzIEiUPArxpDV7G1vqybG+Hc7FDYeCEw7M53ysa3dt2XfW7NnY2/vx7pbZ6T6Wrbn2quX5J1JxZnMcidnWHAUnMgZ8kEAa7NKkU+jyFkeVICqtOUU0ZauES6PQk4HTUQpAJHyAKLYMXBEw2sACh4IahEWrzScctLBoMMC7nVMS6zRsQ55EVZ51KrRiWZuCj0D4mU15zJMZuPI0BeA2pP6wxur9jlR80Faqv4SEX7F5z/msfX0opkd0ej6/QEB91C5', 'eJxNkEsOwjAMRK8SZZ2F3ebjcBWEooK6Y1dAQoi740kciUUjZzJ+HvfjW7vdt+NozZ+cv74f++GDU/W13Z97V8+JgksSXK7ByRpcKcExsx6EigjXPN7gSQmqQF2Ci1pUdHdBn5JaCywML40eJrVKNBIvShcUvFrXMKxzHvApT0WPqFFKH1FGwjI5IyoYBQgeQ5k6VE0ZGJmZulcMigkdTLZMLYaCmtiWqWO7nP/jdxSWh60aJKOtr6SrCo1IiC0LRkaLTTx/hvpzso8v3x/NCVLD'], 'v2': ['eJw9UEEOAiEM/ArZMwdYKQW/YsxGzd72tmpijH93pkUPLWWmHaa8p2W5bZd9X5bpGKbr677uUwxAn5ftsRp6khSDtBhqj6FoDA11zjNTd7QnXiyBL+RTQePBKQdQaGfBySROCc6KkDyY/3BO6lStrsQQJcEL1RANZAeobDZfEFIUSlE24t5k2GtliNuI+bB3ISJAC/tnZ/OM/t7cEAXNRh7WpYwxM4URrb8d7BfqeJCDpqTksu2GJOwe/8H/0+JhD3MDgm2cNZ8/Xz2gUWI=', 'eJw1UEFuAzEI/Iq1Zx88G9vgfqWqVmmUW26bVqqq/r0MkINtGGYGzO92HLfH9TyPY3sr2+fP835utRj6fX183R19H62WobXMYcde2WsBLEGzaMAQQ5UMqaUvFkyilAmpF17TSgz2lpmsEAMSSu12JIVGFYTr6CRZMk0h1pcDdckhaLokpnK71rPLmCGhLycE7Fr6ojSPJq8ROAUcAA3hS09p4QC0XAElcAej6OXlgqypvTqzQpEiAF+Xc6dkyVv733wL0WfPCRY3iRWfmPj4+wckilJp']})

c = NamedArray([])
d = NamedArray([])
c_prime = NamedArray([])
d_prime = NamedArray([])


eqs = equations()
const = {}

v0 = [elements.load_element('eJxNjkEOAiEMRa/SsGZBZ2jpeBVjyGhmNzvUxBjv7i84iQtI+9+j5R1qve1ra7WGE4Xr6761EAnpc90fW0/PeYkkFqlMkTihYC64pjQix5zkl4g6nwdSoAJSOJJ5jTxjgOKYiym5bcN0Ij6Z2YfxX+d4QVPg67HK/a5p/8E8dgiwYnZ23Y73cvl8ARqIL/8=', 1), elements.load_element('eJw1jsEOwyAMQ38l4syBUAJhvzJNqJt6641t0jTt3+dQenBlxX02X9faY197b81dyN0/z607T7i+1/21jes1VU+inrJ4Yo6etMCExVOCMlJleDsyfilqJiEZBpEEiI2xhhAnrcFyfMro48nLcmLl2BwLUDHJIc2GYIQjn03gKpA6ZqexV6l1yO33Bz6sMCM=', 1)]
c = c.append('v0', v0, True)

v1 = [elements.load_element('eJxFTjsOwjAMvYqV2UPc5uNwFVRFBXXrFkBCiLvznERicOz3s/Nxtd7PvbVa3YXc7f04mmMC+9rP59HZayhMUZmyoDJTAQ7oIiuTLjZ4pgRWE4CP9viBOqtmgS9ZaJlDXv8Ve85OQAzrNMh0Rz9VEfOJjoB9Szx0zfNqsA1QCrrKOC5iQ9y+P/DaL9k=', 1), elements.load_element('eJw1js0OAiEMhF+l4cyhQyg/vooxZDV72xtqYozvbgvLAdL5Ou3061p7HFvvrbkLufvnuXfnSel7O177oNdYPUnxlJInsIqkD8iTmCjajaqLOQKrPU4Itg+mbCYELcRTNh/GFjaTWAUd06LgFCMBGL0ws7ISySsDE8oKrWVtzlNUPk9iu1Vuvz+5GjCd', 1)]
c = c.append('v1', v1, True)

v2 = [elements.load_element('eJw9UM1uwzAIfhUrZx8gCQbvVaYq6qreeks3aZr27uMDugMJ/v4M/lmO4/a4nudxLG9t+fh+3s+lN0e/ro/Pe6DvQr2J9TZmb7r3xqsDU/3gxSy9mTM7ygHRUtEKFj7UwIHSI/U3VygIcq/Bw4zPLFoy0TaA3kyqyyOJGRdQOKBYvRNPm/ZCgiOqIXGTBqz/gi2H2bdcyOyl9WjZM0+lwNjfFcrpwF5GWdgewqHZx3B4hojVNDCP2sRGTYa8US8YTGzPVM44gR98+f0D6S5SZQ==', 2), elements.load_element('eJxFUEkOwjAQ+0qUcw6Z7MNXEIoK6q23AhJC/J3ZKIdUtmdiu3n7OW/bsu9z+pPz19d93X1wpD6X7bGKeq4xuDqCaxgcxEokMuikGKmFMPEyeIAKBg0H0Gk05AFkIokBsY5K2AJiM+dh6si8Ro5VxkntB0UVVEctQgCjkaNMUvejJaIKTa4VduZP/LWgvcFR1BUSqAjQ1AliNlla8jIb92bVAXVP+klrjk32KADJXkTiNF1Q4r8saggApohdJ5ua/xly4PL5AuYsUj8=', 2)]
d = d.append('v2', v2, True)

v3 = [elements.load_element('eJxdUMsOAiEM/JWGMwe6QAF/xRiymr3tbdXEGP/dPsCDh1KYzrRT3q73274eR+/uBO76um+H88Doc90fm6LnHDzk6qFwpmw5Rw9NsMUDIl+UlDgYILIoZGQMYbAwCH/ho8TBJwH+SIxl9FCL5aZlnlxRKKII0cqIDLcyStKnTZF2auyEo9Yp5mqSaPIYFRrzRIoLTp3MwWGxoK0j+2NI5l0vPweqDsyj2Wb+gVJqnDuqSx6QpkP1wJRcLGsDNYdmn/Dy+QIgRVH5', 2), elements.load_element('eJw1ULsOwjAM/JWoc4Y6xI/yKwhVBbGxFZAQ4t/x2WFw4tydz44/07pe79u+r+t0LNPl/bjtUy2Ovrb78xboieda2GpRv2nWWhZPFgALgEDZEWeotVqMkVAt4kh3jUqC4sEgyYsNhA01EUz+dtbSDfWQ0AyaDo4s2bV7rg6yhyKHc8sKw1vTODB3EBlDgqC5Z7X1ZLXnjEHEER7xsQMOyc7csxtuIh0jm+u0DS0odnnsTMa+IiHOpkT4oY0H1oQV4cu4EaGQsS+h8/cHvkpRFA==', 2)]
d = d.append('v3', v3, True)

c0 = elements.load_element('eJw9UEFuAyEM/AraMwd7A9j0K1W0SqrcctsmUlX1751Zwx4wMIxnxvwu2/b1vO37ti0fabn/fD/2JSeg79vz9TjQzyo5Vc+p9ZysYl1ycuyqAIrxAERFQeNNUAxPuq4sgMsgGilQM6j5ZexQalQTCVAVzGYT8YF4myilBR0ug0Oziudap6ni5vNQIGESTt2nGwUKGShmketo7hKBVWv0HVwVqjRyTkj7WdbRTD5j8CNqGQFUOaedvSUyREALR+8x3mFI/pjThwU/v+n17x+EeVNA', 2)
const['c0'] = c0

c1 = elements.load_element('eJw1UMtuxDAI/BUrZx+MEwzeX1lV0bbaW25pK1XV/vsOjxxIYGYYwP/Lvn8dj/Pc9+VWls+/7+e51AL093H8PB29c6uFtZaBkF4LkdSiAKnhI4gxrQC9qdHjSiAejKQjmS0pMXG3qlNUphnDLFDoim73Azphwz6S0s87FZSM0FLbLsrn2ZLpx2iy5cVlFIRS9LIYaAxx3hRWdgfbCc612FxnFkPCQnv+0cJb2iI2ybV6z3t5zUR9BGDRGM/XI+RgiWPnjHDaNvT3oY/XGxCgUkw=', 2)
const['c1'] = c1

c2 = elements.load_element('eJw1jjEOwzAIRa+CPHswtsF2r1JFVhply+a0UlX17gXTDAh4/4vPx/W+HesYvbsbuMf73IfzIPS1Hs990ntuHqh64OKhSiFGGUiAwJykqyEIYxEDXa5kZFZTgB6KDmHKbL6qNCnQCLZFIcshjNFgLv/8ZJEkYlEDhushNAdlTWj2nd5iXr4/bMovXQ==', 1)
const['c2'] = c2

c3 = elements.load_element('eJw1jksOwjAMRK9iZe2F3ebjchWEooK66y6AhBB3Z9ykiyz8PPOcb6j1sa+t1RouFO6f59YCE+h73V/bQa9xYUrGlDNTKUyW+lONWMwYECgIpOxwYlociA+gOikmrDKoHQARFRTdbG6FyObTmvoZVb+FqJX+VFwpcfwE3QxbUY9iY3L24ujJsOV0+/0B0HUvwA==', 1)
const['c3'] = c3

t = elements.load_element('eJxNVUGOGzEM+0qQcw62Z2zJ/UpRBNtib3vbtkBR9O81KcqZw0wytmRJFEX/vT+fPz7ePj+fz/uX2/37n5/vn/fHba3+fvv49c7Vr70+bt0fN1u/Zo/bXI8Vfa+n1rXp+FPWzoDliQ/8metP49bUMoz7sZ70HGunl7Sr6+UNDut1HuEEk7HOPh0Wp17Y6bLqHYtDfsgSCSEXXztzhsXI7D2+fXmeSLHUnWdTsqe9zukrkk/ly9gDoeoRCbDU2loeVLusfFkNfJQeNaJocx1kIyqyQ8F3CGuBcC1Hnl6Z3Ih84dVZrILQoUUwPEgYBwA4L/HNdGs1BeQX/Jk4GtVNDUMbAQ9OQE6AjKZEuelcpt4DfiTFppYoCxEAXoDCV22Bvwn3qSOIODruyhtGqAln+akmuvBbdjPxY4ctFt0F/pgKyJ5ZFOCJci2CICqvds2O5wwFzwIAOU2IuWXn05FUbZu9u4tNs4EMCIypm559DKqgt6QQCxoybMnqI5oALo7MxlUY8AgsulhaleWZ05UDGqw8VVLNiWhCJVuL2GTOiBbFULU4rcudVGIB9TUvRTyvGlh6gkaW80AuNXFpjxGiwBHcJTKM1iUVLUeYvZovenGOp+h9iOJD/bXMOvjgu+0a6shNhnY5hfxPcQm/If5YErjHQt9Kc0gpUjZY/YjfmJsa/MuWeU59uTQHpIIR8xs5aC0s9pRQRgirn685CzSb1AWTGE3dUIhZyMiz5ZSBESwjMlQLSwj9IiMpAOgiCDnlGv2vAoC5sVEI7EUpIf/kf4hQ127VDp2rhBkLBButj7k4Qxks26whpTRvPtWLSM15zc23eCKdffbUnKBvhEw4k4QAfgs8iVAkWCMJUSUGnvFSP8SnLkIDqL5xzjvSU98B9pTeaSqaCDmypJI97DnSmhEEthSAqfF4LUqmdX0UMc2Syuyrrl8TkLxvU9G6Lpu4iFI8Qi2TArwoj9cdMKXV53zdS54XVdxmVeMzN+EODUJLHcy7J+AR3LAPle8X3ufFo9q+/fsPPXmYHg==', 3)
const['t'] = t
pis = [
    UnamedArray([
        [
            elements.load_element('eJxFj0EOAiEMRa9CZs2CMlCKVzGGjGZ2sxs1Mca7208ZXVCg7X/9fU+t3bZl31ubTm66vu7rPnmn2eeyPdaePefgXRbvyuydVO8oaIILHvqrWhFUaVREH0mrWY+ohCgjCIJ+Oy1pf9SbrT3rkWiygu5INooZqohQzUCSw4AMLUamMQYQGMqABM3W7peODHzWH7JbSsYs/EfBeY5mi8KxNTSg/DYv3UoeyAhPdewSDFICdGxm+9IosinSPKCinbUMFiagE6sBx3T5fAGjy1EU', 2),
            elements.load_element('eJw1UEEOAiEM/ArhzIEiheJXjCGr2Zu3VRNj/LsdCgfIMB2m03597/fHdhy9+7Pzt89zP3xwyr63x2sf7IVjcCzBlRpcxWnBUdSr6YNLcJK0CAHwSbkKgQIiAYqLKvNVR42VTmDgSUsDc1JUGEDFsn4ZjR7V+hCpOItphSeBRMzLoM3qClIV1GgKznriHErfuZlva1azrkkz5jVRE8sJac0WZwxAcbRLc03JOmEzwwDrkbmejOgR/lTMjccweWUm+zwaFgxA198fCKpR4Q==', 2),
        ],
        [
            elements.load_element('eJw9UMEOwyAI/RXj2YOvFbH7lWUx3dJbb92WLMv+faDYA4LweDz4+lof+3octfqL8/fPczt8cJJ9r/tra9krxeCoBJfFyhQc4hzcwmKSAJJmsj4aQaIk9SJeGxGlY1nGxwJWPCAwEhNPQsex/zslhJzIoHGMhuLaRBU1neDJyAF5ChsSESZbR6WuimHYohToxVQ6Lw+lINPA1Bdq6/FgJl1zLGMbqikysd2o3SCbWJ47e9NUzhFTHODFrtcGZerc6rNUMm6/P9QqUj0=', 2),
            elements.load_element('eJxVUEkOwjAM/ErUcw5xWjcOX0EoKqi33gpICPF3PLEBcfASLzPjPIfWLtuy760NhzCcH9d1H2LQ6n3ZbmuvHjnFwBLDrFaKRtgcAyU4GtXl9H2qm6saxyAahdHxjb6VyaEmg2MtFvHVPkqJ4EZHLxWvZJjcW1mBsxFQzlaV5F0T85cxhkff5MnxoICVT5RYVMGkeckWiYBN4kJwM49GAD3IIVq6HNVVi+1JcSaijxxoAxMY8RvEhid+hVOpq/V3JMaB3j+TTq83Lg1R3A==', 2),
        ],
    ]),
]
thetas = [
    UnamedArray([
        [
            elements.load_element('eJw1jsEOAiEMRH+l4dwDRaDFXzGGrGZve0NNjPHfnS7rhU6HN20/off7tozRezhTuL0f6whMcF/L9lx395IbUzEmjUz5xCRS0ZgLdCpMlryRiVT/hdFAmCIKTyKEZhf7A8RgW/OczpxIgcDE4oj4yJSObRIBNNBNZ1IStpV6gPsNSNX/PMcklnmmodZy/f4AQGcwHw==', 1),
            elements.load_element('eJxFjsEOAiEMRH+l4cxhi5SCv2I2ZDV72xtqYoz/7hSbeKC0bzLTvkPvt2Mbo/dwpnB93fcRIoE+t+OxT3rJLZLUSHqKVPBLicScrVi3AFeJ1BZIYqBaKV5U8UxigJTcwEv7hTFDb9MBrxoVH/5BBbhiYVUHTX1ISFUogszs0MRim+3WeaZY6vr5An+rMHU=', 1),
        ],
        [
            elements.load_element('eJwtjksKwzAMRK8ivPbC8k9Or1KKSUN22TktlNK7dxR5Y5in8ZO+rvftWMfo3d3IPT/nPpwn0Pd6vPaL3vPiqTRPtXjiUBHYk1QNmEgw0AAaK4wAqMpstaRQ/6PNDCIgJSjVh5Opq0wJ8qKDGExSrlWgWSyYMZtI4jxI5kG2AjQnq9fy+P0BgdwvUw==', 1),
            elements.load_element('eJxFjs0OAiEMhF+l4cxhi/y0vorZkNXsbW+oiTG+u1PAeGDa+dJpebtab8fWWq3uTO76uu/NeQJ9bsdj7/QS1VMSTzmjsqeCmuEVPMpkCa944uUEYZkkYNLSeaSZ1QSdYLbMnC6WMwnBhE06S2M5c5hI/ku6YEv8OTtkRuwgkoKkyvhWTuvnCyNZMBc=', 1),
        ],
    ]),
]

eq = Equation([c2, c3], [c0, c1], [[elements.ZpElement.zero(), elements.ZpElement.zero()], [elements.ZpElement.zero(), elements.ZpElement.zero()]], t, 3)
eqs.append(eq)
v=verify(crs, eqs, c, c_prime, d, d_prime, pis, thetas)
print(v)
