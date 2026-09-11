

import pubchempy as pcp

name = "Theobromine"

try:
    compounds = pcp.get_compounds(name, namespace="name")

    print("Number of results:", len(compounds))

    if compounds:
        compound = compounds[0]

        print("CID:", compound.cid)
        print("Molecular weight:", compound.molecular_weight)
        print("Molecular formula:", compound.molecular_formula)
        print("SMILES:", compound.smiles)
    else:
        print("No results found for:", name)

except Exception as e:
    print("Error:", type(e).__name__)
    print(e)

