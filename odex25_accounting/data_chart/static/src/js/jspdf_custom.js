(function (P) {
    'use strict';
    var O = 'addImage_',
        X = ['jpeg', 'jpg', 'png'],
        U = function (g) {
            var j = this.internal.newObject(),
                m = this.internal.write,
                n = this.internal.putStream;
            g['n'] = j;
            m('<</Type /XObject');
            m('/Subtype /Image');
            m('/Width ' + g['w']);
            m('/Height ' + g['h']);
            if (g['cs'] === this.color_spaces.INDEXED) {
                m('/ColorSpace [/Indexed /DeviceRGB ' + (g['pal'].length / 3 - 1) + ' ' + ('smask' in g ? j + 2 : j + 1) + ' 0 R]');
            } else {
                m('/ColorSpace /' + g['cs']);
                if (g['cs'] === this.color_spaces.DEVICE_CMYK) {
                    m('/Decode [1 0 1 0 1 0 1 0]');
                }
            }
            m('/BitsPerComponent ' + g['bpc']);
            if ('f' in g) {
                m('/Filter /' + g['f']);
            }
            if ('dp' in g) {
                m('/DecodeParms <<' + g['dp'] + '>>');
            }
            if ('trns' in g && g['trns'].constructor == Array) {
                var o = '',
                    q = 0,
                    s = g['trns'].length;
                for (; q < s; q++) o += (g['trns'][q] + ' ' + g['trns'][q] + ' ');
                m('/Mask [' + o + ']');
            }
            if ('smask' in g) {
                m('/SMask ' + (j + 1) + ' 0 R');
            }
            m('/Length ' + g['data'].length + '>>');
            n(g['data']);
            m('endobj');
            if ('smask' in g) {
                var t = '/Predictor 15 /Colors 1 /BitsPerComponent ' + g['bpc'] + ' /Columns ' + g['w'];
                var v = {
                    'w': g['w'],
                    'h': g['h'],
                    'cs': 'DeviceGray',
                    'bpc': g['bpc'],
                    'dp': t,
                    'data': g['smask']
                };
                if ('f' in g) v.f = g['f'];
                U.call(this, v);
            }
            if (g['cs'] === this.color_spaces.INDEXED) {
                this.internal.newObject();
                m('<< /Length ' + g['pal'].length + '>>');
                n(this.arrayBufferToBinaryString(new Uint8Array(g['pal'])));
                m('endobj');
            }
        },
        Y = function () {
            var g = this.internal.collections[O + 'images'];
            for (var j in g) {
                U.call(this, g[j]);
            }
        },
        W = function () {
            var g = this.internal.collections[O + 'images'],
                j = this.internal.write,
                m;
            for (var n in g) {
                m = g[n];
                j('/I' + m['i'], m['n'], '0', 'R');
            }
        },
        Q = function (g) {
            if (g && typeof g === 'string') g = g.toUpperCase();
            return g in P.image_compression ? g : P.image_compression.NONE;
        },
        s0 = function () {
            var g = this.internal.collections[O + 'images'];
            if (!g) {
                this.internal.collections[O + 'images'] = g = {};
                this.internal.events.subscribe('putResources', Y);
                this.internal.events.subscribe('putXobjectDict', W);
            }
            return g;
        },
        k0 = function (n) {
            var o = 0;
            if (n) {
                o = Object.keys ? Object.keys(n).length : (function (g) {
                    var j = 0;
                    for (var m in g) {
                        if (g.hasOwnProperty(m)) {
                            j++;
                        }
                    }
                    return j;
                })(n);
            }
            return o;
        },
        m0 = function (g) {
            return typeof g === 'undefined' || g === null;
        },
        j0 = function (g) {
            return typeof g === 'string' && P.sHashCode(g);
        },
        e0 = function (g) {
            return X.indexOf(g) === -1;
        },
        R = function (g) {
            return typeof P['process' + g.toUpperCase()] !== 'function';
        },
        S = function (g) {
            return typeof g === 'object' && g.nodeType === 1;
        },
        y0 = function (g, j, m) {
            if (g.nodeName === 'IMG' && g.hasAttribute('src')) {
                var n = '' + g.getAttribute('src');
                if (!m && n.indexOf('data:image/') === 0) return n;
                if (!j && /\.png(?:[?#].*)?$/i.test(n)) j = 'png';
            }
            if (g.nodeName === 'CANVAS') {
                var o = g;
            } else {
                var o = document.createElement('canvas');
                o.width = g.clientWidth || g.width;
                o.height = g.clientHeight || g.height;
                var q = o.getContext('2d');
                if (!q) {
                    throw ('addImage requires canvas to be supported by browser.');
                }
                if (m) {
                    var s, t, v, H, z, I, K, M = Math.PI / 180,
                        N;
                    if (typeof m === 'object') {
                        s = m.x;
                        t = m.y;
                        v = m.bg;
                        m = m.angle;
                    }
                    N = m * M;
                    H = Math.abs(Math.cos(N));
                    z = Math.abs(Math.sin(N));
                    I = o.width;
                    K = o.height;
                    o.width = K * z + I * H;
                    o.height = K * H + I * z;
                    if (isNaN(s)) s = o.width / 2;
                    if (isNaN(t)) t = o.height / 2;
                    q.clearRect(0, 0, o.width, o.height);
                    q.fillStyle = v || 'white';
                    q.fillRect(0, 0, o.width, o.height);
                    q.save();
                    q.translate(s, t);
                    q.rotate(N);
                    q.drawImage(g, -(I / 2), -(K / 2));
                    q.rotate(-N);
                    q.translate(-s, -t);
                    q.restore();
                } else {
                    q.drawImage(g, 0, 0, o.width, o.height);
                }
            }
            return o.toDataURL(('' + j).toLowerCase() == 'png' ? 'image/png' : 'image/jpeg');
        },
        f0 = function (g, j) {
            var m;
            if (j) {
                for (var n in j) {
                    if (g === j[n].alias) {
                        m = j[n];
                        break;
                    }
                }
            }
            return m;
        },
        v0 = function (g, j, m) {
            if (!g && !j) {
                g = -96;
                j = -96;
            }
            if (g < 0) {
                g = (-1) * m['w'] * 72 / g / this.internal.scaleFactor;
            }
            if (j < 0) {
                j = (-1) * m['h'] * 72 / j / this.internal.scaleFactor;
            }
            if (g === 0) {
                g = j * m['w'] / m['h'];
            }
            if (j === 0) {
                j = g * m['h'] / m['w'];
            }
            return [g, j];
        },
        z0 = function (g, j, m, n, o, q, s) {
            var t = v0.call(this, m, n, o),
                v = this.internal.getCoordinateString,
                H = this.internal.getVerticalCoordinateString;
            m = t[0];
            n = t[1];
            s[q] = o;
            this.internal.write('q', v(m), '0 0', v(n), v(g), H(j + n), 'cm /I' + o['i'], 'Do Q');
        };
    P.color_spaces = {
        DEVICE_RGB: 'DeviceRGB',
        DEVICE_GRAY: 'DeviceGray',
        DEVICE_CMYK: 'DeviceCMYK',
        CAL_GREY: 'CalGray',
        CAL_RGB: 'CalRGB',
        LAB: 'Lab',
        ICC_BASED: 'ICCBased',
        INDEXED: 'Indexed',
        PATTERN: 'Pattern',
        SEPERATION: 'Seperation',
        DEVICE_N: 'DeviceN'
    };
    P.decode = {
        DCT_DECODE: 'DCTDecode',
        FLATE_DECODE: 'FlateDecode',
        LZW_DECODE: 'LZWDecode',
        JPX_DECODE: 'JPXDecode',
        JBIG2_DECODE: 'JBIG2Decode',
        ASCII85_DECODE: 'ASCII85Decode',
        ASCII_HEX_DECODE: 'ASCIIHexDecode',
        RUN_LENGTH_DECODE: 'RunLengthDecode',
        CCITT_FAX_DECODE: 'CCITTFaxDecode'
    };
    P.image_compression = {
        NONE: 'NONE',
        FAST: 'FAST',
        MEDIUM: 'MEDIUM',
        SLOW: 'SLOW'
    };
    P.sHashCode = function (m) {
        return Array.prototype.reduce && m.split("").reduce(function (g, j) {
            g = ((g << 5) - g) + j.charCodeAt(0);
            return g & g;
        }, 0);
    };
    P.isString = function (g) {
        return typeof g === 'string';
    };
    P.extractInfoFromBase64DataURI = function (g) {
        return /^data:([\w]+?\/([\w]+?));base64,(.+?)$/g.exec(g);
    };
    P.supportsArrayBuffer = function () {
        return typeof ArrayBuffer !== 'undefined' && typeof Uint8Array !== 'undefined';
    };
    P.isArrayBuffer = function (g) {
        if (!this.supportsArrayBuffer()) return false;
        return g instanceof ArrayBuffer;
    };
    P.isArrayBufferView = function (g) {
        if (!this.supportsArrayBuffer()) return false;
        if (typeof Uint32Array === 'undefined') return false;
        return (g instanceof Int8Array || g instanceof Uint8Array || (typeof Uint8ClampedArray !== 'undefined' && g instanceof Uint8ClampedArray) || g instanceof Int16Array || g instanceof Uint16Array || g instanceof Int32Array || g instanceof Uint32Array || g instanceof Float32Array || g instanceof Float64Array);
    };
    P.binaryStringToUint8Array = function (g) {
        var j = g.length,
            m = new Uint8Array(j);
        for (var n = 0; n < j; n++) {
            m[n] = g.charCodeAt(n);
        }
        return m;
    };
    P.arrayBufferToBinaryString = function (g) {
        if (this.isArrayBuffer(g)) g = new Uint8Array(g);
        var j = '',
            m = g.byteLength;
        for (var n = 0; n < m; n++) {
            j += String.fromCharCode(g[n]);
        }
        return j;
    };
    P.arrayBufferToBase64 = function (g) {
        var j = '',
            m = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/',
            n = new Uint8Array(g),
            o = n.byteLength,
            q = o % 3,
            s = o - q,
            t, v, H, z, I;
        for (var K = 0; K < s; K = K + 3) {
            I = (n[K] << 16) | (n[K + 1] << 8) | n[K + 2];
            t = (I & 16515072) >> 18;
            v = (I & 258048) >> 12;
            H = (I & 4032) >> 6;
            z = I & 63;
            j += m[t] + m[v] + m[H] + m[z];
        }
        if (q == 1) {
            I = n[s];
            t = (I & 252) >> 2;
            v = (I & 3) << 4;
            j += m[t] + m[v] + '==';
        } else if (q == 2) {
            I = (n[s] << 8) | n[s + 1];
            t = (I & 64512) >> 10;
            v = (I & 1008) >> 4;
            H = (I & 15) << 2;
            j += m[t] + m[v] + m[H] + '=';
        }
        return j;
    };
    P.createImageInfo = function (g, j, m, n, o, q, s, t, v, H, z, I) {
        var K = {
            alias: t,
            w: j,
            h: m,
            cs: n,
            bpc: o,
            i: s,
            data: g
        };
        if (q) K.f = q;
        if (v) K.dp = v;
        if (H) K.trns = H;
        if (z) K.pal = z;
        if (I) K.smask = I;
        return K;
    };
    P.addImage = function (g, j, m, n, o, q, s, t, v) {
        'use strict';
        if (typeof j !== 'string') {
            var H = q;
            q = o;
            o = n;
            n = m;
            m = j;
            j = H;
        }
        if (typeof g === 'object' && !S(g) && "imageData" in g) {
            var z = g;
            g = z.imageData;
            j = z.format || j;
            m = z.x || m || 0;
            n = z.y || n || 0;
            o = z.w || o;
            q = z.h || q;
            s = z.alias || s;
            t = z.compression || t;
            v = z.rotation || z.angle || v;
        }
        if (isNaN(m) || isNaN(n)) {
            console.error('jsPDF.addImage: Invalid coordinates', arguments);
            throw new Error('Invalid coordinates passed to jsPDF.addImage');
        }
        var I = s0.call(this),
            K;
        if (!(K = f0(g, I))) {
            var M;
            if (S(g)) g = y0(g, j, v);
            if (m0(s)) s = j0(g);
            if (!(K = f0(s, I))) {
                if (this.isString(g)) {
                    var N = this.extractInfoFromBase64DataURI(g);
                    if (N) {
                        j = N[2];
                        g = atob(N[3]);
                    } else {
                        if (g.charCodeAt(0) === 0x89 && g.charCodeAt(1) === 0x50 && g.charCodeAt(2) === 0x4e && g.charCodeAt(3) === 0x47) j = 'png';
                    }
                }
                j = (j || 'JPEG').toLowerCase();
                if (e0(j)) throw new Error('addImage currently only supports formats ' + X + ', not \'' + j + '\'');
                if (R(j)) throw new Error('please ensure that the plugin for \'' + j + '\' support is added');
                if (this.supportsArrayBuffer()) {
                    M = g;
                    g = this.binaryStringToUint8Array(g);
                }
                K = this['process' + j.toUpperCase()](g, k0(I), s, Q(t), M);
                if (!K) throw new Error('An unkwown error occurred whilst processing the image');
            }
        }
        z0.call(this, m, n, o, q, K, K.i, I);
        return this;
    };
    var C0 = function (g) {
            'use strict';
            var j, m, n;
            if (!g.charCodeAt(0) === 0xff || !g.charCodeAt(1) === 0xd8 || !g.charCodeAt(2) === 0xff || !g.charCodeAt(3) === 0xe0 || !g.charCodeAt(6) === 'J'.charCodeAt(0) || !g.charCodeAt(7) === 'F'.charCodeAt(0) || !g.charCodeAt(8) === 'I'.charCodeAt(0) || !g.charCodeAt(9) === 'F'.charCodeAt(0) || !g.charCodeAt(10) === 0x00) {
                throw new Error('getJpegSize requires a binary string jpeg file');
            }
            var o = g.charCodeAt(4) * 256 + g.charCodeAt(5),
                q = 4,
                s = g.length;
            while (q < s) {
                q += o;
                if (g.charCodeAt(q) !== 0xff) {
                    throw new Error('getJpegSize could not find the size of the image');
                }
                if (g.charCodeAt(q + 1) === 0xc0 || g.charCodeAt(q + 1) === 0xc1 || g.charCodeAt(q + 1) === 0xc2 || g.charCodeAt(q + 1) === 0xc3 || g.charCodeAt(q + 1) === 0xc4 || g.charCodeAt(q + 1) === 0xc5 || g.charCodeAt(q + 1) === 0xc6 || g.charCodeAt(q + 1) === 0xc7) {
                    m = g.charCodeAt(q + 5) * 256 + g.charCodeAt(q + 6);
                    j = g.charCodeAt(q + 7) * 256 + g.charCodeAt(q + 8);
                    n = g.charCodeAt(q + 9);
                    return [j, m, n];
                } else {
                    q += 2;
                    o = g.charCodeAt(q) * 256 + g.charCodeAt(q + 1);
                }
            }
        },
        Z = function (g) {
            var j = (g[0] << 8) | g[1];
            if (j !== 0xFFD8) throw new Error('Supplied data is not a JPEG');
            var m = g.length,
                n = (g[4] << 8) + g[5],
                o = 4,
                q, s, t, v;
            while (o < m) {
                o += n;
                q = I0(g, o);
                n = (q[2] << 8) + q[3];
                if ((q[1] === 0xC0 || q[1] === 0xC2) && q[0] === 0xFF && n > 7) {
                    q = I0(g, o + 5);
                    s = (q[2] << 8) + q[3];
                    t = (q[0] << 8) + q[1];
                    v = q[4];
                    return {
                        width: s,
                        height: t,
                        numcomponents: v
                    };
                }
                o += 2;
            }
            throw new Error('getJpegSizeFromBytes could not find the size of the image');
        },
        I0 = function (g, j) {
            return g.subarray(j, j + 5);
        };
    P.processJPEG = function (g, j, m, n, o) {
        'use strict';
        var q = this.color_spaces.DEVICE_RGB,
            s = this.decode.DCT_DECODE,
            t = 8,
            v;
        if (this.isString(g)) {
            v = C0(g);
            return this.createImageInfo(g, v[0], v[1], v[3] == 1 ? this.color_spaces.DEVICE_GRAY : q, t, s, j, m);
        }
        if (this.isArrayBuffer(g)) g = new Uint8Array(g);
        if (this.isArrayBufferView(g)) {
            v = Z(g);
            g = o || this.arrayBufferToBinaryString(g);
            return this.createImageInfo(g, v.width, v.height, v.numcomponents == 1 ? this.color_spaces.DEVICE_GRAY : q, t, s, j, m);
        }
        return null;
    };
    P.processJPG = function () {
        return this.processJPEG.apply(this, arguments);
    };
})(jsPDF.API);