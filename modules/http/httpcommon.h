/***************************************************************************
 *
 * Copyright (c) 2000-2015 BalaBit IT Ltd, Budapest, Hungary
 * Copyright (c) 2015-2017 BalaSys IT Ltd, Budapest, Hungary
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 ***************************************************************************/

#ifndef ZORP_MODULES_HTTPCOMMON_H_INCLUDED
#define ZORP_MODULES_HTTPCOMMON_H_INCLUDED

typedef struct _HttpTransfer HttpTransfer;
typedef struct _HttpProxy HttpProxy;

typedef gboolean (*HttpTransferPreambleFunc)(HttpProxy *self, gboolean stacked, GString *preamble);

#endif /* ZORP_MODULES_HTTPCOMMON_H_INCLUDED */
