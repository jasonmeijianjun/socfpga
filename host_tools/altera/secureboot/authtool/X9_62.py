from pyasn1.type import univ, namedtype, tag

class ECVersion(univ.Integer): pass
class ECPrivateKey(univ.OctetString): pass

# FieldID
class X9_62_FieldID(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('fieldType', univ.ObjectIdentifier()),
        namedtype.NamedType('parameters', univ.Any())
    )

# Curve
class X9_62_Curve(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('a', univ.OctetString()),
        namedtype.NamedType('b', univ.OctetString()),
        namedtype.OptionalNamedType('seed', univ.BitString())
    )

# SpecifiedECDomain
class ECParameters(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('version', univ.Integer()),
        namedtype.NamedType('fieldID', X9_62_FieldID()),
        namedtype.NamedType('curve', X9_62_Curve()),
        namedtype.NamedType('base', univ.OctetString()),
        namedtype.NamedType('order', univ.Integer()),
        namedtype.OptionalNamedType('cofactor', univ.Integer())
    )
        
class ECPKParameters(univ.Choice):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('named_curve', univ.ObjectIdentifier()),
        namedtype.NamedType('parameters', ECParameters()),
        namedtype.NamedType('implicitlyCA', univ.Null())
    )
    
class ECPublicKey(univ.BitString): pass

class ECPrivateKey(univ.Sequence):
    componentType = namedtype.NamedTypes(
        namedtype.NamedType('version', ECVersion()),
        namedtype.NamedType('privateKey', ECPrivateKey()),
        namedtype.OptionalNamedType('parameters', ECPKParameters().subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 0))),
        namedtype.OptionalNamedType('publicKey', ECPublicKey().subtype(implicitTag=tag.Tag(tag.tagClassContext, tag.tagFormatConstructed, 1)))
    )


def algo_oid_to_name(algo_oid):
    """Map public key algorithm OID to friendly name string used by OpenSSL."""

    lookup = {
            univ.ObjectIdentifier('1.2.840.10045.3.1.7'): "prime256v1",
            univ.ObjectIdentifier('1.3.132.0.34'): "secp384r1",
        }

    if algo_oid in lookup:
        return lookup[algo_oid]
    else:
        return "unknown"
